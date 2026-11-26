import math

from engine.math.vector import Vector3


class CharacterController:

    def __init__(
        self,
        physics_world,
        terrain_generator,
        city_generator=None,
        position=None,
        walk_speed=5.5,
        sprint_speed=9.5,
        jump_strength=8.5,
        acceleration=24.0,
        deceleration=30.0,
        eye_height=1.65,
        collision_radius=0.45
        
    ):

        # ======================================
        # SYSTEM REFERENCES
        # ======================================

        self.physics = physics_world
        self.terrain = terrain_generator
        self.city = city_generator

        # ======================================
        # CAMERA REFERENCES
        # ======================================

        self.camera_orbit_yaw = -90.0
        self.camera_orbit_pitch = -12.0
        
        self.camera_min_pitch = -65.0
        self.camera_max_pitch = 45.0

        # ======================================
        # CHARACTER POSITION
        # ======================================

        self.position = (
            position.copy()
            if position is not None
            else Vector3(0.0, 0.0, 0.0)
        )

        self.previous_position = self.position.copy()

        # ======================================
        # MOVEMENT SETTINGS
        # ======================================

        self.walk_speed = float(walk_speed)
        self.sprint_speed = float(sprint_speed)

        self.acceleration = float(acceleration)
        self.deceleration = float(deceleration)

        self.jump_strength = float(jump_strength)

        self.eye_height = float(eye_height)
        self.collision_radius = float(collision_radius)

        # ======================================
        # VELOCITY
        # ======================================

        self.horizontal_velocity = Vector3()
        self.vertical_velocity = 0.0

        # ======================================
        # CHARACTER STATE
        # ======================================

        self.is_grounded = False
        self.is_moving = False
        self.is_sprinting = False
        self.is_jumping = False

        self.facing_yaw = -90.0

        # ======================================
        # PHYSICS
        # ======================================

        self.fixed_delta_time = (
            self.physics.get_fixed_delta_time()
        )

        self.accumulator = 0.0
        self.max_substeps = 8

        # ======================================
        # CAMERA SETTINGS
        # ======================================

        self.camera_distance = 6.0
        self.camera_height = 2.2
        self.camera_target_height = 1.45
        self.camera_shoulder_offset = 0.35
        self.camera_smoothing = 12.0

        # ======================================
        # INITIAL GROUND POSITION
        # ======================================

        ground_height = self.get_ground_height(
            self.position.x,
            self.position.z
        )

        self.position.y = ground_height
        self.previous_position = self.position.copy()

        self.is_grounded = True

        print("[CharacterController] Initialized.")
        print(f"[CharacterController] Position: {self.position}")
        print("[CharacterController] Mode: Third Person")
        print("[CharacterController] Movement: Camera Relative")

    # ======================================
    # GROUND HEIGHT
    # ======================================

    def get_ground_height(self, x, z):

        if self.terrain is None:
            return 0.0

        return float(
            self.terrain.get_height(x, z)
        )

    # ======================================
    # INPUT DIRECTION
    # ======================================

    def get_movement_direction(self, input_system, camera):
        direction = Vector3()

        yaw = math.radians(self.camera_orbit_yaw)

        forward = Vector3(
            math.cos(yaw),
            0.0,
            math.sin(yaw)
        ).normalized()

        right = Vector3(
            -math.sin(yaw),
            0.0,
            math.cos(yaw)
        ).normalized()

        if input_system.is_key_down(0x57):  # W
            direction += forward

        if input_system.is_key_down(0x53):  # S
            direction -= forward

        if input_system.is_key_down(0x44):  # D
            direction += right

        if input_system.is_key_down(0x41):  # A
            direction -= right

        if direction.length_squared() > 1.0:
            direction = direction.normalized()

        return direction

    # ======================================
    # HORIZONTAL MOVEMENT
    # ======================================

    def update_horizontal_movement(
        self,
        input_system,
        camera,
        delta_time
    ):

        direction = self.get_movement_direction(
            input_system,
            camera
        )

        self.is_moving = (
            direction.length_squared() > 0.001
        )

        self.is_sprinting = (
            self.is_moving
            and input_system.is_key_down(0x10)
        )

        target_speed = (
            self.sprint_speed
            if self.is_sprinting
            else self.walk_speed
        )

        target_velocity = direction * target_speed

        if self.is_moving:

            change = self.acceleration * delta_time

        else:

            change = self.deceleration * delta_time

        # Smooth acceleration and deceleration
        difference = (
            target_velocity - self.horizontal_velocity
        )

        difference_length = difference.length()

        if difference_length > change:

            difference = (
                difference.normalized() * change
            )

        self.horizontal_velocity += difference

        # Rotate character towards movement direction
        if self.is_moving:

            target_yaw = math.degrees(
                math.atan2(direction.z, direction.x)
            )

            self.facing_yaw = self.rotate_towards(
                self.facing_yaw,
                target_yaw,
                720.0 * delta_time
            )

    # ======================================
    # ROTATION INTERPOLATION
    # ======================================

    @staticmethod
    def rotate_towards(current, target, max_degrees):

        difference = (
            (target - current + 180.0) % 360.0
        ) - 180.0

        difference = max(
            -max_degrees,
            min(max_degrees, difference)
        )

        return current + difference

    # ======================================
    # HORIZONTAL COLLISION
    # ======================================

    def resolve_horizontal_collision(self):

        if self.city is None:
            return

        resolver = getattr(
            self.city,
            "resolve_circle_collision",
            None
        )

        if resolver is None:
            return

        result = resolver(
            self.position.x,
            self.position.z,
            radius=self.collision_radius
        )

        if result is None:
            return

        if isinstance(result, tuple) and len(result) >= 2:

            self.position.x = float(result[0])
            self.position.z = float(result[1])

    # ======================================
    # GRAVITY AND GROUND COLLISION
    # ======================================

    def update_vertical_movement(self, delta_time):

        ground_height = self.get_ground_height(
            self.position.x,
            self.position.z
        )

        self.vertical_velocity = (
            self.physics.apply_gravity(
                self.vertical_velocity,
                delta_time
            )
        )

        self.position.y += (
            self.vertical_velocity * delta_time
        )

        (
            self.position.y,
            self.vertical_velocity,
            self.is_grounded
        ) = self.physics.resolve_ground(
            self.position.y,
            self.vertical_velocity,
            ground_height
        )

        self.is_jumping = (
            not self.is_grounded
            and self.vertical_velocity > 0.0
        )

    # ======================================
    # JUMP
    # ======================================

    def jump(self):

        if not self.is_grounded:
            return False

        self.vertical_velocity = self.jump_strength
        self.is_grounded = False
        self.is_jumping = True

        return True

    # ======================================
    # FIXED PHYSICS STEP
    # ======================================

    def physics_step(
        self,
        input_system,
        camera,
        delta_time,
        jump_pressed=False
    ):

        self.previous_position = self.position.copy()

        # Horizontal movement
        self.update_horizontal_movement(
            input_system,
            camera,
            delta_time
        )

        self.position.x += (
            self.horizontal_velocity.x * delta_time
        )

        self.position.z += (
            self.horizontal_velocity.z * delta_time
        )

        # World collision
        self.resolve_horizontal_collision()

        # Jump
        if jump_pressed and self.is_grounded:
            self.jump()

        # Vertical physics
        self.update_vertical_movement(delta_time)

    # ======================================
    # MAIN UPDATE
    # ======================================

    def update(
        self,
        input_system,
        camera,
        delta_time
    ):

        if delta_time <= 0.0:
            return

        delta_time = min(float(delta_time), 0.25)

        self.accumulator += delta_time

        jump_pressed = input_system.is_key_pressed(0x20)

        steps = 0

        while (
            self.accumulator >= self.fixed_delta_time
            and steps < self.max_substeps
        ):

            self.physics_step(
                input_system,
                camera,
                self.fixed_delta_time,
                jump_pressed
            )

            # Jump input is consumed only once
            jump_pressed = False

            self.accumulator -= self.fixed_delta_time
            steps += 1

        # Avoid unlimited physics backlog
        if steps >= self.max_substeps:
            self.accumulator = min(
                self.accumulator,
                self.fixed_delta_time
            )

    # ======================================
    # THIRD PERSON CAMERA
    # ======================================

    def update_camera(self, camera, delta_time):
        target = self.position + Vector3(
            0.0,
            self.camera_target_height,
            0.0
        )

        yaw = math.radians(self.camera_orbit_yaw)
        pitch = math.radians(self.camera_orbit_pitch)

        forward = Vector3(
            math.cos(yaw) * math.cos(pitch),
            math.sin(pitch),
            math.sin(yaw) * math.cos(pitch)
        ).normalized()

        right = Vector3(
            -math.sin(yaw),
            0.0,
            math.cos(yaw)
        ).normalized()

        desired_position = (
            target
            - forward * self.camera_distance
            + right * self.camera_shoulder_offset
        )

        smoothing = 1.0 - math.exp(
            -self.camera_smoothing * delta_time
        )

        camera.position = camera.position.lerp(
            desired_position,
            smoothing
        )

        direction = (
            target - camera.position
        ).normalized()

        camera.yaw = math.degrees(
            math.atan2(direction.z, direction.x)
        )

        camera.pitch = math.degrees(
            math.asin(
                max(-1.0, min(1.0, direction.y))
            )
        )

        camera.update_vectors()

    # ======================================
    # CAMERA POSITION
    # ======================================

    def get_camera_position(self):

        return self.position + Vector3(
            0.0,
            self.camera_target_height,
            0.0
        )

    # ======================================
    # CHARACTER INFORMATION
    # ======================================

    def get_position(self):
        return self.position.copy()

    def get_velocity(self):

        return Vector3(
            self.horizontal_velocity.x,
            self.vertical_velocity,
            self.horizontal_velocity.z
        )

    def get_facing_yaw(self):
        return self.facing_yaw

    def get_speed(self):
        return self.horizontal_velocity.length()

    def is_on_ground(self):
        return self.is_grounded

    # ======================================
    # TELEPORT
    # ======================================

    def teleport(self, position):

        self.position = position.copy()

        self.previous_position = self.position.copy()

        self.horizontal_velocity = Vector3()
        self.vertical_velocity = 0.0

        self.position.y = self.get_ground_height(
            self.position.x,
            self.position.z
        )

        self.is_grounded = True
        self.is_jumping = False

        self.accumulator = 0.0

    # ======================================
    # CAMER ROTATION
    # ======================================

    def rotate_camera(self, mouse_dx, mouse_dy, sensitivity=0.12):

        self.camera_orbit_yaw += mouse_dx * sensitivity
        self.camera_orbit_pitch -= mouse_dy * sensitivity

        self.camera_orbit_pitch = max(
            self.camera_min_pitch,
            min(self.camera_max_pitch, self.camera_orbit_pitch)
        )

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        self.horizontal_velocity = Vector3()
        self.vertical_velocity = 0.0

        print("[CharacterController] Shutdown complete.")