
class WorldObjectRenderer:

    def __init__(self, renderer):

        self.renderer = renderer

        self.initialized = True

        self.rendered_objects = 0
        self.skipped_objects = 0

        print("[WorldObjectRenderer] Initialized.")

    # ======================================
    # RENDER OBJECTS
    # ======================================

    def render(
        self,
        object_manager,
        shader,
        camera
    ):

        if not self.initialized:
            return

        if object_manager is None:
            return

        if shader is None or camera is None:
            return

        shader.use()

        # Camera matrices
        shader.set_matrix4(
            "uView",
            camera.get_view_matrix()
        )

        shader.set_matrix4(
            "uProjection",
            camera.get_projection_matrix()
        )

        self.rendered_objects = 0
        self.skipped_objects = 0

        objects = object_manager.get_all_objects()

        for game_object in objects:

            # Skip invalid objects
            if not game_object.initialized:
                self.skipped_objects += 1
                continue

            # Skip inactive objects
            if not game_object.active:
                self.skipped_objects += 1
                continue

            # Skip invisible objects
            if not game_object.visible:
                self.skipped_objects += 1
                continue

            # Skip objects without mesh
            if game_object.mesh is None:
                self.skipped_objects += 1
                continue

            # Object transformation
            shader.set_matrix4(
                "uModel",
                game_object.get_matrix()
            )

            # Object color
            shader.set_vector4(
                "uColor",
                *game_object.color
            )

            # Draw object
            self.renderer.draw_mesh(
                game_object.mesh,
                shader
            )

            self.rendered_objects += 1

    # ======================================
    # STATISTICS
    # ======================================

    def get_rendered_count(self):
        return self.rendered_objects

    def get_skipped_count(self):
        return self.skipped_objects

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        if not self.initialized:
            return

        self.renderer = None

        self.initialized = False

        self.rendered_objects = 0
        self.skipped_objects = 0

        print("[WorldObjectRenderer] Shutdown complete.")