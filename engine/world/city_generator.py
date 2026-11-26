from engine.graphics.mesh import Mesh


class CityGenerator:

    def __init__(self, gpu_context, terrain_generator):
        self.gpu = gpu_context
        self.terrain = terrain_generator
        self.chunk_colliders = {}  # (cx, cz) -> list of (min_x, min_z, max_x, max_z, top_y)

    @staticmethod
    def _rand(seed):
        seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
        return seed, (seed / 4294967295.0)

    @staticmethod
    def _add_box(vertices, indices, colors, cx, cy, cz, sx, sy, sz, color):
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        base = len(vertices) // 3

        box_verts = [
            # Front
            cx - hx, cy - hy, cz + hz,  cx + hx, cy - hy, cz + hz,
            cx + hx, cy + hy, cz + hz,  cx - hx, cy + hy, cz + hz,
            # Back
            cx + hx, cy - hy, cz - hz,  cx - hx, cy - hy, cz - hz,
            cx - hx, cy + hy, cz - hz,  cx + hx, cy + hy, cz - hz,
            # Left
            cx - hx, cy - hy, cz - hz,  cx - hx, cy - hy, cz + hz,
            cx - hx, cy + hy, cz + hz,  cx - hx, cy + hy, cz - hz,
            # Right
            cx + hx, cy - hy, cz + hz,  cx + hx, cy - hy, cz - hz,
            cx + hx, cy + hy, cz - hz,  cx + hx, cy + hy, cz + hz,
            # Top
            cx - hx, cy + hy, cz + hz,  cx + hx, cy + hy, cz + hz,
            cx + hx, cy + hy, cz - hz,  cx - hx, cy + hy, cz - hz,
            # Bottom
            cx - hx, cy - hy, cz - hz,  cx + hx, cy - hy, cz - hz,
            cx + hx, cy - hy, cz + hz,  cx - hx, cy - hy, cz + hz,
        ]
        vertices.extend(box_verts)

        shades = [0.95, 0.85, 0.80, 0.90, 1.05, 0.60]
        for face in range(6):
            b = base + face * 4
            indices.extend([b, b + 1, b + 2, b + 2, b + 3, b])
            s = shades[face]
            for _ in range(4):
                colors.extend([color[0] * s, color[1] * s, color[2] * s])

    def generate_chunk_city(self, chunk):
        key = (chunk.chunk_x, chunk.chunk_z)
        self.chunk_colliders[key] = []

        if not self.terrain.is_in_city(chunk.center_x, chunk.center_z):
            return None

        vertices = []
        indices = []
        colors = []

        seed = (chunk.chunk_x * 73856093 ^ chunk.chunk_z * 19349663 ^ self.terrain.seed) & 0xFFFFFFFF

        # A chunk belsejében (az utaktól beljebb) 2x2 épülettelket generálunk
        margin = 9.5
        inner_size = chunk.size - margin * 2.0
        lot_step = inner_size * 0.5

        palette = [
            (0.62, 0.65, 0.70),  # Modern üveg-acél
            (0.78, 0.72, 0.64),  # Vice City pasztell homok
            (0.84, 0.68, 0.72),  # Art Deco rózsaszínes
            (0.55, 0.68, 0.74),  # Tengerkék irodaház
            (0.45, 0.47, 0.52),  # Sötét beton torony
        ]

        for lz in range(2):
            for lx in range(2):
                seed, r_type = self._rand(seed)
                seed, r_h = self._rand(seed)
                seed, r_w = self._rand(seed)
                seed, r_d = self._rand(seed)
                seed, r_col = self._rand(seed)

                cx = chunk.origin_x + margin + (lx + 0.5) * lot_step
                cz = chunk.origin_z + margin + (lz + 0.5) * lot_step
                ground_y = self.terrain.get_height(cx, cz)

                # 15% eséllyel kis városi park pálmafákkal
                if r_type < 0.15:
                    for p in range(3):
                        seed, px_off = self._rand(seed)
                        seed, pz_off = self._rand(seed)
                        tx = cx + (px_off - 0.5) * 10.0
                        tz = cz + (pz_off - 0.5) * 10.0
                        ty = self.terrain.get_height(tx, tz)
                        # Törzs
                        self._add_box(vertices, indices, colors, tx, ty + 3.0, tz, 0.45, 6.0, 0.45, (0.42, 0.28, 0.16))
                        # Pálmalevelek
                        self._add_box(vertices, indices, colors, tx, ty + 6.1, tz, 3.6, 0.35, 0.9, (0.15, 0.58, 0.20))
                        self._add_box(vertices, indices, colors, tx, ty + 6.1, tz, 0.9, 0.35, 3.6, (0.18, 0.62, 0.22))
                    continue

                w = 11.0 + r_w * 7.5
                d = 11.0 + r_d * 7.5
                dist_center = (cx * cx + cz * cz) ** 0.5
                downtown_boost = max(0.4, 1.4 - dist_center / 220.0)
                h = (12.0 + r_h * 34.0) * downtown_boost

                wall_color = palette[int(r_col * len(palette)) % len(palette)]

                # Fő épülettest
                self._add_box(vertices, indices, colors, cx, ground_y + h * 0.5, cz, w, h, d, wall_color)

                # Tetőfelépítmény / antenna felhőkarcolókon
                if h > 26.0:
                    self._add_box(vertices, indices, colors, cx, ground_y + h + 1.5, cz, w * 0.55, 3.0, d * 0.55, (0.35, 0.37, 0.40))
                    self._add_box(vertices, indices, colors, cx, ground_y + h + 5.5, cz, 0.35, 5.0, 0.35, (0.95, 0.20, 0.35))

                # Világító ablaksorok az épület oldalain (magas színérték -> shader emissive)
                floors = int(h // 4.0)
                for fl in range(1, floors):
                    wy = ground_y + fl * 4.0
                    seed, lit = self._rand(seed)
                    win_col = (1.15, 1.08, 0.85) if lit > 0.35 else (0.20, 0.28, 0.36)
                    self._add_box(vertices, indices, colors, cx, wy, cz + d * 0.5 + 0.06, w * 0.78, 1.1, 0.1, win_col)
                    self._add_box(vertices, indices, colors, cx, wy, cz - d * 0.5 - 0.06, w * 0.78, 1.1, 0.1, win_col)
                    self._add_box(vertices, indices, colors, cx + w * 0.5 + 0.06, wy, cz, 0.1, 1.1, d * 0.78, win_col)
                    self._add_box(vertices, indices, colors, cx - w * 0.5 - 0.06, wy, cz, 0.1, 1.1, d * 0.78, win_col)

                # Ütközési doboz mentése
                self.chunk_colliders[key].append((
                    cx - w * 0.5,
                    cz - d * 0.5,
                    cx + w * 0.5,
                    cz + d * 0.5,
                    ground_y + h
                ))

        # Utcai lámpák a sarkokon
        for corner_x in (chunk.origin_x + 6.5, chunk.origin_x + chunk.size - 6.5):
            for corner_z in (chunk.origin_z + 6.5, chunk.origin_z + chunk.size - 6.5):
                gy = self.terrain.get_height(corner_x, corner_z)
                self._add_box(vertices, indices, colors, corner_x, gy + 2.5, corner_z, 0.22, 5.0, 0.22, (0.25, 0.27, 0.30))
                self._add_box(vertices, indices, colors, corner_x, gy + 5.0, corner_z, 0.75, 0.25, 0.75, (1.25, 1.15, 0.85))

        if not vertices:
            return None

        return Mesh(self.gpu, vertices, indices, colors)

    def resolve_circle_collision(self, x, z, radius=0.6):
        for colliders in self.chunk_colliders.values():
            for min_x, min_z, max_x, max_z, _ in colliders:
                closest_x = max(min_x, min(x, max_x))
                closest_z = max(min_z, min(z, max_z))
                dx = x - closest_x
                dz = z - closest_z
                dist_sq = dx * dx + dz * dz
                if dist_sq < radius * radius:
                    dist = dist_sq ** 0.5
                    if dist > 1e-6:
                        overlap = radius - dist
                        x += (dx / dist) * overlap
                        z += (dz / dist) * overlap
                    else:
                        x += radius
        return x, z

    def clear_chunk(self, key):
        self.chunk_colliders.pop(key, None)