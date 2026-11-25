
import math

from engine.math.vector import Vector3
from engine.math.matrix import Matrix4


class Camera:

    def __init__(
        self,
        position=None,
        fov=70.0,
        aspect_ratio=16.0 / 9.0,
        near=0.1,
        far=1000.0
    ):

        # Camera position
        self.position = position or Vector3(0.0, 0.0, 3.0)

        # Camera rotation
        self.yaw = -90.0
        self.pitch = 0.0

        # Projection settings
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        # Camera direction
        self.world_up = Vector3(0.0, 1.0, 0.0)

        self.front = Vector3(0.0, 0.0, -1.0)
        self.right = Vector3(1.0, 0.0, 0.0)
        self.up = Vector3(0.0, 1.0, 0.0)

        self.update_vectors()

    # ======================================
    # UPDATE CAMERA VECTORS
    # ======================================

    def update_vectors(self):

        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)

        direction = Vector3(
            math.cos(yaw) * math.cos(pitch),
            math.sin(pitch),
            math.sin(yaw) * math.cos(pitch)
        )

        self.front = direction.normalized()

        self.right = self.front.cross(
            self.world_up
        ).normalized()

        self.up = self.right.cross(
            self.front
        ).normalized()

    # ======================================
    # ROTATION
    # ======================================

    def rotate(self, mouse_dx, mouse_dy, sensitivity=0.1):

        self.yaw += mouse_dx * sensitivity
        self.pitch -= mouse_dy * sensitivity

        self.pitch = max(
            -89.0,
            min(89.0, self.pitch)
        )

        self.update_vectors()

    # ======================================
    # MOVEMENT
    # ======================================

    def move_forward(self, amount):

        self.position = self.position + self.front * amount

    def move_backward(self, amount):

        self.position = self.position - self.front * amount

    def move_right(self, amount):

        self.position = self.position + self.right * amount

    def move_left(self, amount):

        self.position = self.position - self.right * amount

    def move_up(self, amount):

        self.position.y += amount

    def move_down(self, amount):

        self.position.y -= amount

    # ======================================
    # VIEW MATRIX
    # ======================================

    def get_view_matrix(self):

        target = self.position + self.front

        return Matrix4.look_at(
            self.position,
            target,
            self.up
        )

    # ======================================
    # PROJECTION MATRIX
    # ======================================

    def get_projection_matrix(self):

        return Matrix4.perspective(
            self.fov,
            self.aspect_ratio,
            self.near,
            self.far
        )

    # ======================================
    # SETTINGS
    # ======================================

    def set_aspect_ratio(self, width, height):

        if height <= 0:
            return

        self.aspect_ratio = width / height

    def set_fov(self, fov):

        self.fov = max(1.0, min(120.0, fov))

    def set_position(self, position):

        self.position = position.copy()

    def get_position(self):

        return self.position.copy()