
import math

from .vector import Vector3, Vector4


class Matrix3:
    def __init__(self, values=None):
        if values is None:
            self.data = [
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0
            ]
        else:
            if len(values) != 9:
                raise ValueError("Matrix3 requires 9 values.")
            self.data = [float(v) for v in values]

    def get(self, row, col):
        return self.data[col * 3 + row]

    def set(self, row, col, value):
        self.data[col * 3 + row] = float(value)

    @staticmethod
    def identity():
        return Matrix3()

    def transpose(self):
        result = Matrix3([0.0] * 9)

        for row in range(3):
            for col in range(3):
                result.set(row, col, self.get(col, row))

        return result

    def __mul__(self, other):
        if not isinstance(other, Matrix3):
            return NotImplemented

        result = Matrix3([0.0] * 9)

        for row in range(3):
            for col in range(3):
                value = 0.0

                for k in range(3):
                    value += self.get(row, k) * other.get(k, col)

                result.set(row, col, value)

        return result

    def transform_vector(self, vector):
        return Vector3(
            self.get(0, 0) * vector.x +
            self.get(0, 1) * vector.y +
            self.get(0, 2) * vector.z,

            self.get(1, 0) * vector.x +
            self.get(1, 1) * vector.y +
            self.get(1, 2) * vector.z,

            self.get(2, 0) * vector.x +
            self.get(2, 1) * vector.y +
            self.get(2, 2) * vector.z
        )

    def to_list(self):
        return self.data.copy()

    def __repr__(self):
        return f"Matrix3({self.data})"


class Matrix4:
    def __init__(self, values=None):
        if values is None:
            self.data = [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0
            ]
        else:
            if len(values) != 16:
                raise ValueError("Matrix4 requires 16 values.")
            self.data = [float(v) for v in values]

    def get(self, row, col):
        return self.data[col * 4 + row]

    def set(self, row, col, value):
        self.data[col * 4 + row] = float(value)

    @staticmethod
    def identity():
        return Matrix4()

    @staticmethod
    def translation(position):
        result = Matrix4()

        result.set(0, 3, position.x)
        result.set(1, 3, position.y)
        result.set(2, 3, position.z)

        return result

    @staticmethod
    def scale(value):
        result = Matrix4([0.0] * 16)

        if isinstance(value, Vector3):
            x, y, z = value.x, value.y, value.z
        else:
            x = y = z = float(value)

        result.set(0, 0, x)
        result.set(1, 1, y)
        result.set(2, 2, z)
        result.set(3, 3, 1.0)

        return result

    @staticmethod
    def rotation_x(degrees):
        angle = math.radians(degrees)
        c = math.cos(angle)
        s = math.sin(angle)

        result = Matrix4()
        result.set(1, 1, c)
        result.set(1, 2, -s)
        result.set(2, 1, s)
        result.set(2, 2, c)

        return result

    @staticmethod
    def rotation_y(degrees):
        angle = math.radians(degrees)
        c = math.cos(angle)
        s = math.sin(angle)

        result = Matrix4()
        result.set(0, 0, c)
        result.set(0, 2, s)
        result.set(2, 0, -s)
        result.set(2, 2, c)

        return result

    @staticmethod
    def rotation_z(degrees):
        angle = math.radians(degrees)
        c = math.cos(angle)
        s = math.sin(angle)

        result = Matrix4()
        result.set(0, 0, c)
        result.set(0, 1, -s)
        result.set(1, 0, s)
        result.set(1, 1, c)

        return result

    @staticmethod
    def perspective(fov_degrees, aspect, near, far):
        if aspect <= 0:
            raise ValueError("Aspect ratio must be positive.")
        if near <= 0 or far <= near:
            raise ValueError("Invalid near/far clipping planes.")
        if not 0 < fov_degrees < 180:
            raise ValueError("FOV must be between 0 and 180 degrees.")

        f = 1.0 / math.tan(math.radians(fov_degrees) / 2.0)

        result = Matrix4([0.0] * 16)

        result.set(0, 0, f / aspect)
        result.set(1, 1, f)
        result.set(2, 2, (far + near) / (near - far))
        result.set(2, 3, (2.0 * far * near) / (near - far))
        result.set(3, 2, -1.0)

        return result

    @staticmethod
    def look_at(eye, target, up):
        forward = (target - eye).normalized()
        side = forward.cross(up).normalized()
        corrected_up = side.cross(forward)

        if forward.length() == 0 or side.length() == 0:
            raise ValueError("Invalid camera direction or up vector.")

        result = Matrix4([0.0] * 16)

        result.set(0, 0, side.x)
        result.set(0, 1, side.y)
        result.set(0, 2, side.z)
        result.set(0, 3, -side.dot(eye))

        result.set(1, 0, corrected_up.x)
        result.set(1, 1, corrected_up.y)
        result.set(1, 2, corrected_up.z)
        result.set(1, 3, -corrected_up.dot(eye))

        result.set(2, 0, -forward.x)
        result.set(2, 1, -forward.y)
        result.set(2, 2, -forward.z)
        result.set(2, 3, forward.dot(eye))

        result.set(3, 3, 1.0)

        return result

    def transpose(self):
        result = Matrix4([0.0] * 16)

        for row in range(4):
            for col in range(4):
                result.set(row, col, self.get(col, row))

        return result

    def transform_vector4(self, vector):
        return Vector4(
            sum(self.get(0, i) * v for i, v in enumerate(vector.to_tuple())),
            sum(self.get(1, i) * v for i, v in enumerate(vector.to_tuple())),
            sum(self.get(2, i) * v for i, v in enumerate(vector.to_tuple())),
            sum(self.get(3, i) * v for i, v in enumerate(vector.to_tuple()))
        )

    def transform_point(self, point):
        result = self.transform_vector4(
            Vector4(point.x, point.y, point.z, 1.0)
        )

        if abs(result.w) < 1e-8:
            raise ZeroDivisionError("Point transformed to zero W.")

        return Vector3(
            result.x / result.w,
            result.y / result.w,
            result.z / result.w
        )

    def transform_direction(self, direction):
        result = self.transform_vector4(
            Vector4(direction.x, direction.y, direction.z, 0.0)
        )

        return Vector3(result.x, result.y, result.z)

    def __mul__(self, other):
        if not isinstance(other, Matrix4):
            return NotImplemented

        result = Matrix4([0.0] * 16)

        for row in range(4):
            for col in range(4):
                value = 0.0

                for k in range(4):
                    value += self.get(row, k) * other.get(k, col)

                result.set(row, col, value)

        return result

    def to_list(self):
        return self.data.copy()

    def __repr__(self):
        rows = []

        for row in range(4):
            rows.append(
                "[" + ", ".join(
                    f"{self.get(row, col):.3f}"
                    for col in range(4)
                ) + "]"
            )

        return "Matrix4(\n  " + "\n  ".join(rows) + "\n)"