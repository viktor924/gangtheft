import math


class TerrainGenerator:

    def __init__(
        self,
        seed=12345,
        base_height=0.0,
        height_amplitude=14.0,
        noise_scale=0.015,
        octaves=4,
        persistence=0.5,
        lacunarity=2.0,
        block_size=64.0,
        road_width=10.0
    ):
        self.seed = int(seed)
        self.base_height = float(base_height)
        self.height_amplitude = float(height_amplitude)
        self.noise_scale = float(noise_scale)
        self.octaves = int(octaves)
        self.persistence = float(persistence)
        self.lacunarity = float(lacunarity)

        self.block_size = float(block_size)
        self.road_width = float(road_width)
        self.city_radius = 192.0  # A belváros sugara a pálya közepétől

    def _hash_noise(self, x, z):
        n = (x * 374761393 + z * 668265263 + self.seed * 1442695041) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177
        n &= 0xFFFFFFFF
        n ^= n >> 16
        return (n / 4294967295.0) * 2.0 - 1.0

    @staticmethod
    def _fade(t):
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    @staticmethod
    def _lerp(a, b, t):
        return a + (b - a) * t

    def _noise(self, x, z):
        x0 = math.floor(x)
        z0 = math.floor(z)
        tx = self._fade(x - x0)
        tz = self._fade(z - z0)

        n00 = self._hash_noise(x0, z0)
        n10 = self._hash_noise(x0 + 1, z0)
        n01 = self._hash_noise(x0, z0 + 1)
        n11 = self._hash_noise(x0 + 1, z0 + 1)

        return self._lerp(self._lerp(n00, n10, tx), self._lerp(n01, n11, tx), tz)

    def _fbm(self, x, z):
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0.0

        for _ in range(self.octaves):
            total += self._noise(x * frequency, z * frequency) * amplitude
            max_amplitude += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        return total / max_amplitude if max_amplitude > 0.0 else 0.0

    def is_in_city(self, world_x, world_z):
        return abs(world_x) <= self.city_radius and abs(world_z) <= self.city_radius

    def get_road_mask(self, world_x, world_z):
        """Visszaadja: 'road', 'sidewalk', vagy None."""
        if not self.is_in_city(world_x, world_z):
            return None

        half_road = self.road_width * 0.5
        sidewalk_limit = half_road + 2.5

        bx = abs(((world_x + self.block_size * 0.5) % self.block_size) - self.block_size * 0.5)
        bz = abs(((world_z + self.block_size * 0.5) % self.block_size) - self.block_size * 0.5)

        if bx <= half_road or bz <= half_road:
            return "road"
        if bx <= sidewalk_limit or bz <= sidewalk_limit:
            return "sidewalk"
        return None

    def get_city_blend(self, world_x, world_z):
        dist = max(abs(world_x), abs(world_z))
        if dist <= self.city_radius - 16.0:
            return 1.0
        if dist >= self.city_radius + 32.0:
            return 0.0
        t = 1.0 - (dist - (self.city_radius - 16.0)) / 48.0
        return self._fade(max(0.0, min(1.0, t)))

    def get_height(self, world_x, world_z):
        raw_noise = self._fbm(world_x * self.noise_scale, world_z * self.noise_scale)
        natural_height = self.base_height + raw_noise * self.height_amplitude

        # Városban enyhén hullámzó, de vezethető sík terep
        city_height = self.base_height + 0.5 + math.sin(world_x * 0.01) * 0.4 + math.cos(world_z * 0.01) * 0.4
        blend = self.get_city_blend(world_x, world_z)
        height = self._lerp(natural_height, city_height, blend)

        mask = self.get_road_mask(world_x, world_z)
        if mask == "sidewalk":
            height += 0.16
        return height

    def get_surface_color(self, world_x, world_z, height):
        mask = self.get_road_mask(world_x, world_z)
        if mask == "road":
            # Aszfalt és középső sárga felezővonal
            bx = abs(((world_x + self.block_size * 0.5) % self.block_size) - self.block_size * 0.5)
            bz = abs(((world_z + self.block_size * 0.5) % self.block_size) - self.block_size * 0.5)
            if (bx < 0.22 and int(abs(world_z)) % 6 < 3) or (bz < 0.22 and int(abs(world_x)) % 6 < 3):
                return (0.95, 0.78, 0.15)
            return (0.14, 0.15, 0.17)
        if mask == "sidewalk":
            return (0.52, 0.53, 0.55)

        if self.is_in_city(world_x, world_z):
            return (0.20, 0.42, 0.18)

        # Városon kívüli biomok: homokos part, fű, szikla
        if height < -1.5:
            return (0.82, 0.76, 0.54)
        elif height > 6.5:
            return (0.45, 0.44, 0.42)
        return (0.16, 0.46, 0.15)