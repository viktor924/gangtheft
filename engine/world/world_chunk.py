
class WorldChunk:

    def __init__(self, world, chunk_x, chunk_z):

        if not world.is_valid_chunk(chunk_x, chunk_z):
            raise ValueError(
                f"Invalid chunk coordinates: ({chunk_x}, {chunk_z})"
            )

        self.world = world

        self.chunk_x = int(chunk_x)
        self.chunk_z = int(chunk_z)

        self.size = world.chunk_size

        self.origin_x, self.origin_z = world.get_chunk_origin(
            self.chunk_x,
            self.chunk_z
        )

        self.center_x = self.origin_x + self.size / 2.0
        self.center_z = self.origin_z + self.size / 2.0

        self.is_loaded = False
        self.is_generated = False
        self.is_visible = False

    def contains_position(self, x, z):

        return (
            self.origin_x <= x < self.origin_x + self.size
            and
            self.origin_z <= z < self.origin_z + self.size
        )

    def load(self):

        if self.is_loaded:
            return

        self.is_loaded = True

    def unload(self):

        if not self.is_loaded:
            return

        self.is_visible = False
        self.is_loaded = False

    def set_visible(self, visible):

        if visible and not self.is_loaded:
            raise RuntimeError(
                "Cannot show a chunk that is not loaded."
            )

        self.is_visible = bool(visible)