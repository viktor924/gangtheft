import math
from .vector import Vector3
from .matrix import Matrix4


class Transform:
    def __init__(
        self,
        position=None,
        rotation=None,
        scale=None
    ):
        self.position = position.copy() if position else Vector3(0, 0, 0)
        self.rotation = rotation.copy() if rotation else Vector3(0, 0, 0)
        self.scale = scale.copy() if scale else Vector3(1, 1, 1)

        self._matrix_cache = None
        self._dirty = True

    def mark_dirty(self):
        self._dirty = True

    def set_position(self, position):
        self.position = position.copy()
        self.mark_dirty()

    def set_rotation(self, rotation):
        self.rotation = rotation.copy()
        self.mark_dirty()

    def set_scale(self, scale):
        self.scale = scale.copy()
        self.mark_dirty()

    def translate(self, offset):
        self.position += offset
        self.mark_dirty()

    def rotate(self, offset):
        self.rotation += offset
        self.mark_dirty()

    def set_uniform_scale(self, value):
        self.scale = Vector3(value, value, value)
        self.mark_dirty()

    def get_matrix(self):
        if not self._dirty and self._matrix_cache is not None:
            return self._matrix_cache

        translation = Matrix4.translation(self.position)

        rotation_x = Matrix4.rotation_x(self.rotation.x)
        rotation_y = Matrix4.rotation_y(self.rotation.y)
        rotation_z = Matrix4.rotation_z(self.rotation.z)

        scaling = Matrix4.scale(self.scale)

        # Forgatási sorrend: Z -> Y -> X.
        rotation = rotation_z * rotation_y * rotation_x

        # A pont először méreteződik, majd forog, végül eltolódik.
        self._matrix_cache = translation * rotation * scaling

        self._dirty = False

        return self._matrix_cache

    @property
    def forward(self):
        direction = Matrix4.rotation_y(self.rotation.y).transform_direction(
            Vector3(0, 0, -1)
        )
        return direction.normalized()

    @property
    def backward(self):
        return -self.forward

    @property
    def right(self):
        direction = Matrix4.rotation_y(self.rotation.y).transform_direction(
            Vector3(1, 0, 0)
        )
        return direction.normalized()

    @property
    def left(self):
        return -self.right

    @property
    def up(self):
        direction = Matrix4.rotation_x(self.rotation.x).transform_direction(
            Vector3(0, 1, 0)
        )
        return direction.normalized()

    @property
    def down(self):
        return -self.up

    def look_at(self, target):
        direction = target - self.position

        if direction.length() == 0:
            return

        # Y tengely körüli vízszintes forgatás.
        self.rotation.y = -math.degrees(
            math.atan2(direction.x, -direction.z)
        )

        # X tengely körüli függőleges forgatás.
        horizontal = (direction.x ** 2 + direction.z ** 2) ** 0.5

        self.rotation.x = math.degrees(
            math.atan2(direction.y, horizontal)
        )

        self.mark_dirty()

    def copy(self):
        return Transform(
            position=self.position,
            rotation=self.rotation,
            scale=self.scale
        )

    def __repr__(self):
        return (
            f"Transform("
            f"position={self.position}, "
            f"rotation={self.rotation}, "
            f"scale={self.scale})"
        )