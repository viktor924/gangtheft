
import math


class World:

    def __init__(
        self,
        chunk_size=64.0,
        chunks_x=8,
        chunks_z=8
    ):

        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero.")

        if chunks_x <= 0 or chunks_z <= 0:
            raise ValueError("World chunk dimensions must be greater than zero.")

        self.chunk_size = float(chunk_size)

        self.chunks_x = int(chunks_x)
        self.chunks_z = int(chunks_z)

        self.width = self.chunk_size * self.chunks_x
        self.depth = self.chunk_size * self.chunks_z

        self.half_width = self.width / 2.0
        self.half_depth = self.depth / 2.0

        self.initialized = True

        print("[World] World initialized.")

    def world_to_chunk(self, x, z):

        chunk_x = math.floor(
            (x + self.half_width) / self.chunk_size
        )

        chunk_z = math.floor(
            (z + self.half_depth) / self.chunk_size
        )

        return chunk_x, chunk_z

    def get_chunk_origin(self, chunk_x, chunk_z):

        if not self.is_valid_chunk(chunk_x, chunk_z):
            raise ValueError("Invalid chunk coordinates.")

        x = -self.half_width + chunk_x * self.chunk_size
        z = -self.half_depth + chunk_z * self.chunk_size

        return x, z

    def is_valid_chunk(self, chunk_x, chunk_z):

        return (
            0 <= chunk_x < self.chunks_x
            and
            0 <= chunk_z < self.chunks_z
        )

    def is_inside(self, x, z):

        return (
            -self.half_width <= x < self.half_width
            and
            -self.half_depth <= z < self.half_depth
        )