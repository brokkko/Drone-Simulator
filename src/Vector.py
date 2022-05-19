import math


class Vector:

    def __init__(self, x=0., y=0., z=0.):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f'x={self.x} y={self.y} z={self.z}'

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, float):
            return Vector(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, float):
            return Vector(self.x - other, self.y - other, self.z - other)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x / other.x, self.y / other.y, self.z / other.z)
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x / other, self.y / other, self.z / other)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y and self.z == other.z
        elif isinstance(other, float) or isinstance(other, int):
            return self.x == other and self.y == other and self.z == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_xyz(self):
        return self.x, self.y, self.z

    def get_xy(self) -> (int, int):
        return int(self.x), int(self.y)

    def setXYZ(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        return Vector(*self.get_xyz())

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def distance_to(self, vector) -> float:
        return math.sqrt((self.x - vector.x) * (self.x - vector.x)
                         + (self.y - vector.y) * (self.y - vector.y)
                         + (self.z - vector.z) * (self.z - vector.z))

    def rotate_z(self, angle: float):
        tx = self.x
        ty = self.y
        self.x = tx * math.cos(angle) - ty * math.sin(angle)
        self.y = tx * math.sin(angle) + ty * math.cos(angle)
        return self
