
from engine.graphics.mesh import Mesh
from engine.world.terrain_generator import TerrainGenerator
from engine.world.city_generator import CityGenerator


class WorldRenderer:

    def __init__(self, gpu_context, world_manager):

        self.gpu = gpu_context
        self.world_manager = world_manager

        self.chunk_meshes = {}
        self.city_meshes = {}

        self.terrain_generator = TerrainGenerator()
        self.city_generator = CityGenerator(
            gpu_context,
            self.terrain_generator
        )

        self.terrain_resolution = 32

        # Chunk generation queue
        self.pending_chunks = {}

        # Maximum new chunks generated per frame
        self.max_chunks_per_frame = 1

        self.initialized = True

        print("[WorldRenderer] Initialized.")

    # ==================================================
    # TERRAIN GENERATION
    # ==================================================

    def _create_chunk_mesh(self, chunk):

        vertices = []
        colors = []
        indices = []

        x0 = chunk.origin_x
        z0 = chunk.origin_z
        size = chunk.size

        resolution = self.terrain_resolution
        step = size / resolution

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

                colors.extend(
                    self.terrain_generator.get_surface_color(
                        world_x,
                        world_z,
                        height
                    )
                )

        # Generate terrain indices
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

    # ==================================================
    # CHUNK GENERATION
    # ==================================================

    def _generate_chunk(self, chunk):

        key = (
            chunk.chunk_x,
            chunk.chunk_z
        )

        if key in self.chunk_meshes:
            return

        print(
            f"[WorldRenderer] Generating chunk {key}"
        )

        # Generate terrain
        terrain_mesh = self._create_chunk_mesh(chunk)

        # Generate city and collision data
        city_mesh = self.city_generator.generate_chunk_city(
            chunk
        )

        # Store generated meshes
        self.chunk_meshes[key] = terrain_mesh

        if city_mesh is not None:

            self.city_meshes[key] = city_mesh

        print(
            f"[WorldRenderer] Chunk {key} ready."
        )

    # ==================================================
    # CHUNK CLEANUP
    # ==================================================

    def _remove_chunk(self, key):

        if key in self.chunk_meshes:

            self.chunk_meshes[key].close()
            del self.chunk_meshes[key]

        if key in self.city_meshes:

            self.city_meshes[key].close()
            del self.city_meshes[key]

        self.city_generator.clear_chunk(key)

        self.pending_chunks.pop(key, None)

    # ==================================================
    # CHUNK STREAMING
    # ==================================================

    def update(self):

        if not self.initialized:
            return

        loaded_chunks = self.world_manager.get_loaded_chunks()

        active_chunks = {
            (chunk.chunk_x, chunk.chunk_z): chunk
            for chunk in loaded_chunks
        }

        active_keys = set(active_chunks.keys())

        # Remove chunks that are no longer required
        existing_keys = (
            set(self.chunk_meshes.keys())
            | set(self.city_meshes.keys())
        )

        for key in existing_keys:

            if key not in active_keys:
                self._remove_chunk(key)

        # Remove outdated pending requests
        for key in list(self.pending_chunks.keys()):

            if key not in active_keys:
                del self.pending_chunks[key]

        # Add missing chunks to the generation queue
        for key, chunk in active_chunks.items():

            if key in self.chunk_meshes:
                continue

            if key in self.pending_chunks:
                continue

            self.pending_chunks[key] = chunk

        # No work to do
        if not self.pending_chunks:
            return

        # Find player chunk for prioritization
        player_chunk = self.world_manager.player_chunk

        if player_chunk is None:
            return

        player_cx, player_cz = player_chunk

        # Generate nearest chunks first
        sorted_keys = sorted(
            self.pending_chunks.keys(),
            key=lambda key: (
                (key[0] - player_cx) ** 2
                + (key[1] - player_cz) ** 2
            )
        )

        # Generate only a limited number per frame
        for key in sorted_keys[:self.max_chunks_per_frame]:

            chunk = self.pending_chunks.pop(key)

            if key not in active_keys:
                continue

            self._generate_chunk(chunk)

    # ==================================================
    # RENDER
    # ==================================================

    def render(self, renderer, shader, camera, model_matrix):

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

            renderer.draw_mesh(
                mesh,
                shader
            )

        for city_mesh in self.city_meshes.values():

            renderer.draw_mesh(
                city_mesh,
                shader
            )

    # ==================================================
    # SHUTDOWN
    # ==================================================

    def close(self):

        for mesh in self.chunk_meshes.values():
            mesh.close()

        self.chunk_meshes.clear()

        for mesh in self.city_meshes.values():
            mesh.close()

        self.city_meshes.clear()

        self.pending_chunks.clear()

        self.city_generator.chunk_colliders.clear()

        self.initialized = False

        print("[WorldRenderer] Closed.")