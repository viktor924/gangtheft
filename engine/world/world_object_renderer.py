
class ObjectRenderer:

    def __init__(self, renderer):

        self.renderer = renderer

        self.initialized = True
        self.rendered_objects = 0
        self.skipped_objects = 0

        print("[ObjectRenderer] Initialized.")

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

        shader.use()

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

            if not game_object.initialized:
                self.skipped_objects += 1
                continue

            if not game_object.active:
                self.skipped_objects += 1
                continue

            if not game_object.visible:
                self.skipped_objects += 1
                continue

            if game_object.mesh is None:
                self.skipped_objects += 1
                continue

            shader.set_matrix4(
                "uModel",
                game_object.get_matrix()
            )

            shader.set_vector4(
                "uColor",
                *game_object.color
            )

            self.renderer.draw_mesh(
                game_object.mesh,
                shader
            )

            self.rendered_objects += 1

    def get_rendered_count(self):
        return self.rendered_objects

    def get_skipped_count(self):
        return self.skipped_objects

    def close(self):

        if not self.initialized:
            return

        self.renderer = None
        self.initialized = False

        print("[ObjectRenderer] Shutdown complete.")