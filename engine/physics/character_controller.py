
from engine.math.vector import Vector3


class CharacterController:

    def __init__(
        self,
        physics_world,
        terrain_generator,
        position=None,
        walk_speed=5.0,
        sprint_speed=10.0,
        jump_strength=8.0,
        eye_height=1.8
    ):

        self.physics = physics_world
        self.terrain = terrain_generator

        self.position = position or Vector3(0.0, 0.0, 0.0)

        self.walk_speed = float(walk_speed)
        self.sprint_speed = float(sprint_speed)
        self.jump_strength = float(jump_strength)
        self.eye_height = float(eye_height)

        self.vertical_velocity = 0.0

        self.is_grounded = False

        self.air_control = 0.65

        # Place character on terrain
        ground_height = self.terrain.get_height(
            self.position.x,
            self.position.z
        )

        self.position.y = ground_height

        print("[CharacterController] Initialized.")
        print("[CharacterController] Position:", self.position)

    # ======================================
    # MOVEMENT
    # ======================================

    def update(self, input_system, camera, delta_time):

        if delta_time <= 0.0:
            return

        movement = Vector3(0.0, 0.0, 0.0)

        # Horizontal camera directions
        forward = Vector3(
            camera.front.x,
            0.0,
            camera.front.z
        ).normalized()

        right = Vector3(
            camera.right.x,
            0.0,
            camera.right.z
        ).normalized()

        # WASD
        if input_system.is_key_down(0x57):
            movement = movement + forward

        if input_system.is_key_down(0x53):
            movement = movement - forward

        if input_system.is_key_down(0x44):
            movement = movement + right

        if input_system.is_key_down(0x41):
            movement = movement - right

        # Normalize diagonal movement
        if movement.length() > 0.0:
            movement = movement.normalized()

        # Sprint
        speed = self.walk_speed

        if input_system.is_key_down(0x10):
            speed = self.sprint_speed

        # Air control
        if not self.is_grounded:
            speed *= self.air_control

        # Horizontal movement
        self.position = (
            self.position + movement * speed * delta_time
        )

        # ======================================
        # TERRAIN COLLISION
        # ======================================

        ground_height = self.terrain.get_height(
            self.position.x,
            self.position.z
        )

        # Check if character is standing on ground
        if (
            self.position.y <= ground_height + 0.05
            and self.vertical_velocity <= 0.0
        ):

            self.position.y = ground_height
            self.vertical_velocity = 0.0

            self.is_grounded = True

        else:

            self.is_grounded = False

        # ======================================
        # JUMP
        # ======================================

        if (
            self.is_grounded
            and input_system.is_key_pressed(0x20)
        ):

            self.vertical_velocity = self.jump_strength
            self.is_grounded = False

        # ======================================
        # GRAVITY
        # ======================================

        if not self.is_grounded:

            self.vertical_velocity = (
                self.physics.apply_gravity(
                    self.vertical_velocity,
                    delta_time
                )
            )

            self.position.y += (
                self.vertical_velocity * delta_time
            )

        # ======================================
        # GROUND COLLISION RESOLUTION
        # ======================================

        self.position.y, self.vertical_velocity, self.is_grounded = (
            self.physics.resolve_ground(
                self.position.y,
                self.vertical_velocity,
                ground_height
            )
        )

    # ======================================
    # CAMERA POSITION
    # ======================================

    def get_camera_position(self):

        return Vector3(
            self.position.x,
            self.position.y + self.eye_height,
            self.position.z
        )

    # ======================================
    # INFORMATION
    # ======================================

    def get_position(self):
        return self.position

    def is_on_ground(self):
        return self.is_grounded

    def close(self):

        print("[CharacterController] Shutdown complete.")