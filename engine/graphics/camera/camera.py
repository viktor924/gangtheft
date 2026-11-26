
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
        self.position = (
            position.copy()
            if position is not None
            else Vector3(0.0, 0.0, 3.0)
        )

        # Camera rotation
        self.yaw = -90.0
        self.pitch = 0.0

        # Projection settings
        self.fov = float(fov)
        self.aspect_ratio = float(aspect_ratio)
        self.near = float(near)
        self.far = float(far)

        # Camera direction
        self.world_up = Vector3(0.0, 1.0, 0.0)

        self.front = Vector3(0.0, 0.0, -1.0)
        self.right = Vector3(1.0, 0.0, 0.0)
        self.up = Vector3(0.0, 1.0, 0.0)

        # Mouse rotation settings
        self.sensitivity = 0.12

        # Initialize direction vectors
        self.update_vectors()

    # ======================================
    # UPDATE CAMERA VECTORS
    # ======================================

    def update_vectors(self):

        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        direction = Vector3(
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad)
        )

        self.front = direction.normalized()

        self.right = self.front.cross(
            self.world_up
        ).normalized()

        self.up = self.right.cross(
            self.front
        ).normalized()

    # ======================================
    # CAMERA ROTATION
    # ======================================

    def rotate(
        self,
        mouse_dx,
        mouse_dy,
        sensitivity=None
    ):

        if sensitivity is None:
            sensitivity = self.sensitivity

        # Horizontal rotation
        self.yaw += float(mouse_dx) * sensitivity

        # Vertical rotation
        self.pitch -= float(mouse_dy) * sensitivity

        # Prevent camera flipping
        self.pitch = max(
            -89.0,
            min(89.0, self.pitch)
        )

        # Update direction immediately
        self.update_vectors()

    # ======================================
    # CAMERA MOVEMENT
    # ======================================

    def move_forward(self, amount):

        self.position = (
            self.position + self.front * amount
        )

    def move_backward(self, amount):

        self.position = (
            self.position - self.front * amount
        )

    def move_right(self, amount):

        self.position = (
            self.position + self.right * amount
        )

    def move_left(self, amount):

        self.position = (
            self.position - self.right * amount
        )

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
    # CAMERA SETTINGS
    # ======================================

    def set_aspect_ratio(self, width, height):

        if height <= 0:
            return

        self.aspect_ratio = float(width) / float(height)

    def set_fov(self, fov):

        self.fov = max(
            1.0,
            min(120.0, float(fov))
        )

    def set_position(self, position):

        self.position = position.copy()

    def get_position(self):

        return self.position.copy()

    # ======================================
    # CAMERA ROTATION SETTINGS
    # ======================================

    def set_sensitivity(self, sensitivity):

        self.sensitivity = max(
            0.01,
            min(2.0, float(sensitivity))
        )