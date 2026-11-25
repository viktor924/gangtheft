
import math


class TerrainGenerator:

    def __init__(
        self,
        seed=12345,
        base_height=0.0,
        height_amplitude=8.0,
        noise_scale=0.025,
        octaves=4,
        persistence=0.5,
        lacunarity=2.0
    ):

        self.seed = int(seed)

        self.base_height = float(base_height)
        self.height_amplitude = float(height_amplitude)

        self.noise_scale = float(noise_scale)
        self.octaves = int(octaves)

        self.persistence = float(persistence)
        self.lacunarity = float(lacunarity)

        if self.noise_scale <= 0:
            raise ValueError("Noise scale must be positive.")

        if self.octaves <= 0:
            raise ValueError("Octaves must be positive.")

        if self.height_amplitude < 0:
            raise ValueError("Height amplitude cannot be negative.")

        print("[TerrainGenerator] Initialized.")

    # --------------------------------------------------
    # DETERMINISTIC HASH NOISE
    # --------------------------------------------------

    def _hash_noise(self, x, z):

        n = (
            x * 374761393
            + z * 668265263
            + self.seed * 1442695041
        ) & 0xFFFFFFFF

        n = (n ^ (n >> 13)) * 1274126177
        n &= 0xFFFFFFFF

        n ^= n >> 16

        return (n / 4294967295.0) * 2.0 - 1.0

    # --------------------------------------------------
    # SMOOTH INTERPOLATION
    # --------------------------------------------------

    @staticmethod
    def _fade(t):

        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    @staticmethod
    def _lerp(a, b, t):

        return a + (b - a) * t

    # --------------------------------------------------
    # VALUE NOISE
    # --------------------------------------------------

    def _noise(self, x, z):

        x0 = math.floor(x)
        z0 = math.floor(z)

        x1 = x0 + 1
        z1 = z0 + 1

        tx = self._fade(x - x0)
        tz = self._fade(z - z0)

        n00 = self._hash_noise(x0, z0)
        n10 = self._hash_noise(x1, z0)

        n01 = self._hash_noise(x0, z1)
        n11 = self._hash_noise(x1, z1)

        nx0 = self._lerp(n00, n10, tx)
        nx1 = self._lerp(n01, n11, tx)

        return self._lerp(nx0, nx1, tz)

    # --------------------------------------------------
    # FRACTAL BROWNIAN MOTION
    # --------------------------------------------------

    def _fbm(self, x, z):

        total = 0.0

        amplitude = 1.0
        frequency = 1.0

        max_amplitude = 0.0

        for _ in range(self.octaves):

            sample = self._noise(
                x * frequency,
                z * frequency
            )

            total += sample * amplitude

            max_amplitude += amplitude

            amplitude *= self.persistence
            frequency *= self.lacunarity

        if max_amplitude == 0.0:
            return 0.0

        return total / max_amplitude

    # --------------------------------------------------
    # WORLD HEIGHT
    # --------------------------------------------------

    def get_height(self, world_x, world_z):

        sample_x = world_x * self.noise_scale
        sample_z = world_z * self.noise_scale

        noise_value = self._fbm(sample_x, sample_z)

        height = (
            self.base_height
            + noise_value * self.height_amplitude
        )

        return height