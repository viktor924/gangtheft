
from engine.graphics.mesh import Mesh
from engine.world.terrain_generator import TerrainGenerator


class WorldRenderer:

    def __init__(self, gpu_context, world_manager):

        self.gpu = gpu_context
        self.world_manager = world_manager

        self.chunk_meshes = {}

        # Terrain generation
        self.terrain_generator = TerrainGenerator()

        # Number of terrain subdivisions per chunk
        self.terrain_resolution = 16

        # Terrain color
        self.ground_color = (0.16, 0.42, 0.14)

        self.initialized = True

        print("[WorldRenderer] Initialized.")

    # ======================================
    # CREATE CHUNK GEOMETRY
    # ======================================

    def _create_chunk_mesh(self, chunk):

        vertices = []
        colors = []
        indices = []

        x0 = chunk.origin_x
        z0 = chunk.origin_z

        size = chunk.size
        resolution = self.terrain_resolution

        # Distance between terrain vertices
        step = size / resolution

        # Generate terrain vertices
        for z in range(resolution + 1):

            for x in range(resolution + 1):

                world_x = x0 + x * step
                world_z = z0 + z * step

                height = self.terrain_generator.get_height(
                    world_x,
                    world_z
                )

                vertices.extend([
                    world_x,
                    height,
                    world_z
                ])

                colors.extend(self.ground_color)

        # Generate terrain triangles
        for z in range(resolution):

            for x in range(resolution):

                top_left = z * (resolution + 1) + x
                top_right = top_left + 1

                bottom_left = (
                    (z + 1) * (resolution + 1) + x
                )

                bottom_right = bottom_left + 1

                indices.extend([
                    top_left,
                    bottom_right,
                    top_right,

                    top_left,
                    bottom_left,
                    bottom_right
                ])

        return Mesh(
            self.gpu,
            vertices,
            indices,
            colors
        )

    # ======================================
    # UPDATE CHUNKS
    # ======================================

    def update(self):

        loaded_chunks = self.world_manager.get_loaded_chunks()

        active_keys = set()

        for chunk in loaded_chunks:

            key = (
                chunk.chunk_x,
                chunk.chunk_z
            )

            active_keys.add(key)

            if key not in self.chunk_meshes:

                self.chunk_meshes[key] = (
                    self._create_chunk_mesh(chunk)
                )

                print(
                    f"[WorldRenderer] Created terrain mesh "
                    f"for chunk {key}"
                )

        # Release unloaded chunk meshes
        for key in list(self.chunk_meshes.keys()):

            if key not in active_keys:

                self.chunk_meshes[key].close()

                del self.chunk_meshes[key]

                print(
                    f"[WorldRenderer] Released mesh "
                    f"for chunk {key}"
                )

    # ======================================
    # RENDER WORLD
    # ======================================

    def render(
        self,
        renderer,
        shader,
        camera,
        model_matrix
    ):

        if not self.initialized:
            return

        shader.use()

        shader.set_matrix4(
            "uModel",
            model_matrix
        )

        shader.set_matrix4(
            "uView",
            camera.get_view_matrix()
        )

        shader.set_matrix4(
            "uProjection",
            camera.get_projection_matrix()
        )

        shader.set_vector4(
            "uColor",
            1.0,
            1.0,
            1.0,
            1.0
        )

        for mesh in self.chunk_meshes.values():

            renderer.draw_mesh(mesh, shader)

    # ======================================
    # INFORMATION
    # ======================================

    def get_chunk_mesh_count(self):

        return len(self.chunk_meshes)

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        for mesh in self.chunk_meshes.values():
            mesh.close()

        self.chunk_meshes.clear()

        self.initialized = False

        print("[WorldRenderer] Shutdown complete.")