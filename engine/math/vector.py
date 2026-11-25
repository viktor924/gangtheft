
import math


# ============================================================
# VECTOR 2
# ============================================================

class Vector2:

    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented

        return Vector2(
            self.x + other.x,
            self.y + other.y
        )

    def __sub__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented

        return Vector2(
            self.x - other.x,
            self.y - other.y
        )

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented

        return Vector2(
            self.x * scalar,
            self.y * scalar
        )

    def __rmul__(self, scalar):
        return self * scalar

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Vector2 division by zero.")

        return Vector2(
            self.x / scalar,
            self.y / scalar
        )

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __repr__(self):
        return f"Vector2({self.x:.4f}, {self.y:.4f})"

    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return False

        return (
            math.isclose(self.x, other.x) and
            math.isclose(self.y, other.y)
        )

    def length_squared(self):
        return self.x * self.x + self.y * self.y

    def length(self):
        return math.sqrt(self.length_squared())

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def normalized(self):
        magnitude = self.length()

        if magnitude == 0:
            return Vector2()

        return self / magnitude

    def normalize(self):
        magnitude = self.length()

        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude

        return self

    def distance(self, other):
        return (self - other).length()

    def lerp(self, other, amount):
        return self + (other - self) * amount

    def copy(self):
        return Vector2(self.x, self.y)

    def to_tuple(self):
        return (self.x, self.y)


# ============================================================
# VECTOR 3
# ============================================================

class Vector3:

    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        if not isinstance(other, Vector3):
            return NotImplemented

        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other):
        if not isinstance(other, Vector3):
            return NotImplemented

        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented

        return Vector3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar
        )

    def __rmul__(self, scalar):
        return self * scalar

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Vector3 division by zero.")

        return Vector3(
            self.x / scalar,
            self.y / scalar,
            self.z / scalar
        )

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __repr__(self):
        return (
            f"Vector3({self.x:.4f}, "
            f"{self.y:.4f}, {self.z:.4f})"
        )

    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False

        return (
            math.isclose(self.x, other.x) and
            math.isclose(self.y, other.y) and
            math.isclose(self.z, other.z)
        )

    def length_squared(self):
        return (
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )

    def length(self):
        return math.sqrt(self.length_squared())

    def dot(self, other):
        return (
            self.x * other.x +
            self.y * other.y +
            self.z * other.z
        )

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def normalized(self):
        magnitude = self.length()

        if magnitude == 0:
            return Vector3()

        return self / magnitude

    def normalize(self):
        magnitude = self.length()

        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude

        return self

    def distance(self, other):
        return (self - other).length()

    def lerp(self, other, amount):
        return self + (other - self) * amount

    def copy(self):
        return Vector3(self.x, self.y, self.z)

    def to_tuple(self):
        return (self.x, self.y, self.z)


# ============================================================
# VECTOR 4
# ============================================================

class Vector4:

    __slots__ = ("x", "y", "z", "w")

    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def __add__(self, other):
        if not isinstance(other, Vector4):
            return NotImplemented

        return Vector4(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
            self.w + other.w
        )

    def __sub__(self, other):
        if not isinstance(other, Vector4):
            return NotImplemented

        return Vector4(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
            self.w - other.w
        )

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented

        return Vector4(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
            self.w * scalar
        )

    def __rmul__(self, scalar):
        return self * scalar

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Vector4 division by zero.")

        return Vector4(
            self.x / scalar,
            self.y / scalar,
            self.z / scalar,
            self.w / scalar
        )

    def __neg__(self):
        return Vector4(-self.x, -self.y, -self.z, -self.w)

    def __repr__(self):
        return (
            f"Vector4({self.x:.4f}, {self.y:.4f}, "
            f"{self.z:.4f}, {self.w:.4f})"
        )

    def __eq__(self, other):
        if not isinstance(other, Vector4):
            return False

        return (
            math.isclose(self.x, other.x) and
            math.isclose(self.y, other.y) and
            math.isclose(self.z, other.z) and
            math.isclose(self.w, other.w)
        )

    def length_squared(self):
        return (
            self.x * self.x +
            self.y * self.y +
            self.z * self.z +
            self.w * self.w
        )

    def length(self):
        return math.sqrt(self.length_squared())

    def dot(self, other):
        return (
            self.x * other.x +
            self.y * other.y +
            self.z * other.z +
            self.w * other.w
        )

    def normalized(self):
        magnitude = self.length()

        if magnitude == 0:
            return Vector4()

        return self / magnitude

    def normalize(self):
        magnitude = self.length()

        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude
            self.w /= magnitude

        return self

    def distance(self, other):
        return (self - other).length()

    def lerp(self, other, amount):
        return self + (other - self) * amount

    def copy(self):
        return Vector4(self.x, self.y, self.z, self.w)

    def to_tuple(self):
        return (self.x, self.y, self.z, self.w)