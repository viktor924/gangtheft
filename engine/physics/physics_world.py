
class PhysicsWorld:

    def __init__(
        self,
        gravity=-24.0,
        terminal_velocity=-50.0
    ):

        self.gravity = float(gravity)
        self.terminal_velocity = float(terminal_velocity)

        if self.gravity >= 0:
            raise ValueError("Gravity must be negative.")

        if self.terminal_velocity >= 0:
            raise ValueError("Terminal velocity must be negative.")

        self.initialized = True

        print("[PhysicsWorld] Initialized.")
        print(f"[PhysicsWorld] Gravity: {self.gravity}")
        print(
            f"[PhysicsWorld] Terminal velocity: "
            f"{self.terminal_velocity}"
        )

    # ======================================
    # GRAVITY
    # ======================================

    def apply_gravity(self, vertical_velocity, delta_time):

        if delta_time < 0:
            raise ValueError("Delta time cannot be negative.")

        vertical_velocity += self.gravity * delta_time

        # Limit falling speed
        vertical_velocity = max(
            self.terminal_velocity,
            vertical_velocity
        )

        return vertical_velocity

    # ======================================
    # GROUND COLLISION
    # ======================================

    def resolve_ground(
        self,
        position_y,
        vertical_velocity,
        ground_height,
        ground_offset=0.0
    ):

        minimum_height = ground_height + ground_offset

        grounded = False

        if position_y <= minimum_height:

            position_y = minimum_height
            vertical_velocity = 0.0

            grounded = True

        return position_y, vertical_velocity, grounded

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        self.initialized = False

        print("[PhysicsWorld] Shutdown complete.")