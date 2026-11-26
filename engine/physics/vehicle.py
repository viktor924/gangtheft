import math
from engine.math.vector import Vector3
from engine.math.transform import Transform
from engine.graphics.mesh import Mesh


class Vehicle:

    def __init__(self, gpu_context, terrain_generator, city_generator, position, color=(0.90, 0.12, 0.18), is_ai=False):
        self.terrain = terrain_generator
        self.city = city_generator
        self.is_ai = is_ai

        self.transform = Transform(position=position.copy())
        self.yaw = 0.0
        self.speed = 0.0
        self.max_speed = 36.0 if not is_ai else 13.0
        self.acceleration = 22.0
        self.brake_force = 35.0
        self.turn_speed = 115.0
        self.driver = None

        self.mesh = self._build_car_mesh(gpu_context, color)

    def _build_car_mesh(self, gpu_context, body_color):
        vertices, indices, colors = [], [], []

        def add_part(cx, cy, cz, sx, sy, sz, col):
            hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
            base = len(vertices) // 3
            vertices.extend([
                cx - hx, cy - hy, cz + hz, cx + hx, cy - hy, cz + hz, cx + hx, cy + hy, cz + hz, cx - hx, cy + hy, cz + hz,
                cx + hx, cy - hy, cz - hz, cx - hx, cy - hy, cz - hz, cx - hx, cy + hy, cz - hz, cx + hx, cy + hy, cz - hz,
                cx - hx, cy - hy, cz - hz, cx - hx, cy - hy, cz + hz, cx - hx, cy + hy, cz + hz, cx - hx, cy + hy, cz - hz,
                cx + hx, cy - hy, cz + hz, cx + hx, cy - hy, cz - hz, cx + hx, cy + hy, cz - hz, cx + hx, cy + hy, cz + hz,
                cx - hx, cy + hy, cz + hz, cx + hx, cy + hy, cz + hz, cx + hx, cy + hy, cz - hz, cx - hx, cy + hy, cz - hz,
                cx - hx, cy - hy, cz - hz, cx + hx, cy - hy, cz - hz, cx + hx, cy - hy, cz + hz, cx - hx, cy - hy, cz + hz,
            ])
            for face in range(6):
                b = base + face * 4
                indices.extend([b, b + 1, b + 2, b + 2, b + 3, b])
                for _ in range(4):
                    colors.extend(col)

        # Alváz / karosszéria
        add_part(0.0, 0.55, 0.0, 2.0, 0.65, 4.4, body_color)
        # Utastér és sötétített szélvédő
        add_part(0.0, 1.05, -0.2, 1.7, 0.55, 2.2, (0.12, 0.16, 0.22))
        # Első fényszórók (világítanak)
        add_part(-0.65, 0.58, -2.22, 0.42, 0.20, 0.08, (1.4, 1.35, 1.1))
        add_part(0.65, 0.58, -2.22, 0.42, 0.20, 0.08, (1.4, 1.35, 1.1))
        # Hátsó féklámpák
        add_part(-0.65, 0.60, 2.22, 0.45, 0.18, 0.08, (1.4, 0.1, 0.1))
        add_part(0.65, 0.60, 2.22, 0.45, 0.18, 0.08, (1.4, 0.1, 0.1))
        # 4 kerék
        for wx in (-0.98, 0.98):
            for wz in (-1.35, 1.35):
                add_part(wx, 0.35, wz, 0.32, 0.70, 0.70, (0.08, 0.08, 0.09))

        return Mesh(gpu_context, vertices, indices, colors)

    def get_forward(self):
        rad = math.radians(self.yaw)
        return Vector3(-math.sin(rad), 0.0, -math.cos(rad)).normalized()

    def update(self, input_system, delta_time):
        if delta_time <= 0.0:
            return

        if self.driver is not None:
            throttle = 0.0
            if input_system.is_key_down(0x57):  # W
                throttle += 1.0
            if input_system.is_key_down(0x53):  # S
                throttle -= 1.0

            if throttle > 0:
                self.speed += self.acceleration * delta_time
            elif throttle < 0:
                self.speed -= self.brake_force * delta_time
            else:
                self.speed *= max(0.0, 1.0 - 2.2 * delta_time)

            # Kézifék (SPACE)
            if input_system.is_key_down(0x20):
                self.speed *= max(0.0, 1.0 - 6.5 * delta_time)

            self.speed = max(-14.0, min(self.max_speed, self.speed))

            if abs(self.speed) > 0.4:
                steer = 0.0
                if input_system.is_key_down(0x41):  # A
                    steer += 1.0
                if input_system.is_key_down(0x44):  # D
                    steer -= 1.0
                reverse_sign = 1.0 if self.speed >= 0 else -1.0
                self.yaw += steer * self.turn_speed * reverse_sign * delta_time
        elif self.is_ai:
            # Egyszerű városi AI forgalom
            self.speed = self.max_speed
            if abs(self.transform.position.x) > 185.0 or abs(self.transform.position.z) > 185.0:
                self.yaw += 90.0 * delta_time
        else:
            self.speed *= max(0.0, 1.0 - 3.5 * delta_time)

        forward = self.get_forward()
        new_pos = self.transform.position + forward * (self.speed * delta_time)

        # Épület ütközés
        resolved_x, resolved_z = self.city.resolve_circle_collision(new_pos.x, new_pos.z, radius=1.5)
        if abs(resolved_x - new_pos.x) > 0.05 or abs(resolved_z - new_pos.z) > 0.05:
            self.speed *= -0.35
            if self.is_ai:
                self.yaw += 90.0

        new_pos.x = resolved_x
        new_pos.z = resolved_z
        new_pos.y = self.terrain.get_height(new_pos.x, new_pos.z)

        self.transform.set_position(new_pos)
        self.transform.set_rotation(Vector3(0.0, self.yaw, 0.0))

    def close(self):
        if self.mesh:
            self.mesh.close()
            self.mesh = None