
from engine.math.transform import Transform
from engine.math.vector import Vector3


class GameObject:

    _next_id = 1

    def __init__(
        self,
        name="GameObject",
        mesh=None,
        position=None,
        rotation=None,
        scale=None,
        color=(1.0, 1.0, 1.0, 1.0)
    ):

        self.id = GameObject._next_id
        GameObject._next_id += 1

        self.name = str(name)
        self.mesh = mesh

        self.transform = Transform(
            position=position or Vector3(0.0, 0.0, 0.0),
            rotation=rotation or Vector3(0.0, 0.0, 0.0),
            scale=scale or Vector3(1.0, 1.0, 1.0)
        )

        self.color = tuple(color)

        if len(self.color) != 4:
            raise ValueError("GameObject color must contain 4 values.")

        self.visible = True
        self.active = True
        self.initialized = True

        print(
            f"[GameObject] Created: {self.name} "
            f"(ID: {self.id})"
        )

    def set_mesh(self, mesh):
        self.mesh = mesh

    def set_color(self, color):
        color = tuple(color)

        if len(color) != 4:
            raise ValueError("Color must contain 4 values.")

        self.color = color

    def set_visible(self, visible):
        self.visible = bool(visible)

    def set_active(self, active):
        self.active = bool(active)

    def get_position(self):
        return self.transform.position

    def get_transform(self):
        return self.transform

    def get_matrix(self):
        return self.transform.get_matrix()

    def update(self, delta_time):
        if not self.initialized or not self.active:
            return

    def close(self):
        if not self.initialized:
            return

        self.mesh = None
        self.initialized = False

        print(
            f"[GameObject] Destroyed: {self.name} "
            f"(ID: {self.id})"
        )

    def __repr__(self):
        return (
            f"GameObject("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"position={self.transform.position})"
        )