
class PhysicsWorld:

    def __init__(
        self,
        gravity=-24.0,
        terminal_velocity=-60.0,
        fixed_delta_time=1.0 / 60.0,
        max_substeps=8
    ):

        self.gravity = float(gravity)
        self.terminal_velocity = float(terminal_velocity)

        self.fixed_delta_time = float(fixed_delta_time)
        self.max_substeps = int(max_substeps)

        if self.gravity >= 0:
            raise ValueError("Gravity must be negative.")

        if self.terminal_velocity >= 0:
            raise ValueError("Terminal velocity must be negative.")

        if self.fixed_delta_time <= 0:
            raise ValueError("Fixed delta time must be positive.")

        if self.max_substeps < 1:
            raise ValueError("Max substeps must be at least 1.")

        # Simulation state
        self.accumulator = 0.0
        self.simulation_time = 0.0

        self.step_count = 0
        self.initialized = True

        print("[PhysicsWorld] Initialized.")
        print(f"[PhysicsWorld] Gravity: {self.gravity}")
        print(f"[PhysicsWorld] Terminal velocity: {self.terminal_velocity}")
        print(f"[PhysicsWorld] Fixed timestep: {self.fixed_delta_time}")

    # ======================================
    # FIXED TIMESTEP
    # ======================================

    def begin_frame(self, delta_time):

        if not self.initialized:
            return 0

        if delta_time < 0:
            raise ValueError("Delta time cannot be negative.")

        # Prevent huge simulation jumps
        delta_time = min(float(delta_time), 0.25)

        self.accumulator += delta_time

        steps = 0

        while (
            self.accumulator >= self.fixed_delta_time
            and steps < self.max_substeps
        ):

            self.accumulator -= self.fixed_delta_time

            self.simulation_time += self.fixed_delta_time

            self.step_count += 1
            steps += 1

        # Avoid an unlimited backlog after a long frame
        if steps >= self.max_substeps:
            self.accumulator = min(
                self.accumulator,
                self.fixed_delta_time
            )

        return steps

    def get_fixed_delta_time(self):
        return self.fixed_delta_time

    def get_interpolation_alpha(self):

        return min(
            1.0,
            max(0.0, self.accumulator / self.fixed_delta_time)
        )

    # ======================================
    # GRAVITY
    # ======================================

    def apply_gravity(self, vertical_velocity, delta_time):

        if delta_time < 0:
            raise ValueError("Delta time cannot be negative.")

        vertical_velocity += self.gravity * delta_time

        return max(
            self.terminal_velocity,
            vertical_velocity
        )

    # ======================================
    # VELOCITY INTEGRATION
    # ======================================

    def integrate_velocity(
        self,
        velocity,
        acceleration,
        delta_time
    ):

        if delta_time < 0:
            raise ValueError("Delta time cannot be negative.")

        return velocity + acceleration * delta_time

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

            if vertical_velocity < 0.0:
                vertical_velocity = 0.0

            grounded = True

        return (
            position_y,
            vertical_velocity,
            grounded
        )

    # ======================================
    # SIMULATION INFORMATION
    # ======================================

    def get_simulation_time(self):
        return self.simulation_time

    def get_step_count(self):
        return self.step_count

    def reset(self):

        self.accumulator = 0.0
        self.simulation_time = 0.0
        self.step_count = 0

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        self.reset()
        self.initialized = False

        print("[PhysicsWorld] Shutdown complete.")