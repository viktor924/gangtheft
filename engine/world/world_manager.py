
from engine.world.world_chunk import WorldChunk


class WorldManager:

    def __init__(self, world, load_radius=1):

        if load_radius < 0:
            raise ValueError("Load radius cannot be negative.")

        self.world = world
        self.load_radius = int(load_radius)

        self.chunks = {}

        self.player_chunk = None

        print("[WorldManager] Initialized.")

    def get_chunk(self, chunk_x, chunk_z):

        if not self.world.is_valid_chunk(chunk_x, chunk_z):
            return None

        key = (chunk_x, chunk_z)

        if key not in self.chunks:
            self.chunks[key] = WorldChunk(
                self.world,
                chunk_x,
                chunk_z
            )

        return self.chunks[key]

    def update(self, player_x, player_z):

        if not self.world.is_inside(player_x, player_z):
            raise ValueError(
                "Player is outside the world boundaries."
            )

        player_chunk_x, player_chunk_z = (
            self.world.world_to_chunk(player_x, player_z)
        )

        self.player_chunk = (
            player_chunk_x,
            player_chunk_z
        )

        required_chunks = set()

        radius = self.load_radius

        for offset_x in range(-radius, radius + 1):
            for offset_z in range(-radius, radius + 1):

                chunk_x = player_chunk_x + offset_x
                chunk_z = player_chunk_z + offset_z

                if not self.world.is_valid_chunk(
                    chunk_x,
                    chunk_z
                ):
                    continue

                required_chunks.add((chunk_x, chunk_z))

        # Load required chunks
        for key in required_chunks:

            chunk = self.get_chunk(*key)

            if not chunk.is_loaded:
                chunk.load()

            chunk.set_visible(True)

        # Unload chunks outside the loading area
        for key, chunk in self.chunks.items():

            if key not in required_chunks:
                chunk.unload()

        print(
            f"[WorldManager] Player chunk: "
            f"{self.player_chunk}"
        )

        print(
            f"[WorldManager] Active chunks: "
            f"{len(required_chunks)}"
        )

    def unload_all(self):

        for chunk in self.chunks.values():
            chunk.unload()

        print("[WorldManager] All chunks unloaded.")

    def get_loaded_chunks(self):

        return [
            chunk
            for chunk in self.chunks.values()
            if chunk.is_loaded
        ]

    def get_loaded_count(self):

        return len(self.get_loaded_chunks())