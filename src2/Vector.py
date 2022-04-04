import math


class Vector:

    def __init__(self, x, y, z):

        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f'x={self.x} y={self.y}'

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
        elif isinstance(other, float):
            return Vector(self.x * other, self.y * other, self.z * other)

    def get_xyz(self):
        return self.x, self.y, self.z

    def get_xy(self):
        return self.x, self.y

    def copy(self):
        return Vector(*self.get_xyz())

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def distance_to(self, vector):
        return math.sqrt((self.x - vector.x) * (self.x - vector.x)
                         + (self.y - vector.y) * (self.y - vector.y)
                         + (self.z - vector.z) * (self.z - vector.z))

    def rotate_z(self, angle: float):
        tx = self.x
        ty = self.y
        self.x = tx * math.cos(angle) - ty * math.sin(angle)
        self.y = tx * math.sin(angle) + ty * math.cos(angle)
        return self
