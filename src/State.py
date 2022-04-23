from src.Vector import Vector
from typing import Optional


class State:
    def __init__(self, velocity:  Optional[Vector] = None, position: Optional[Vector] = None):

        if velocity and position:
            self.velocity = velocity
            self.position = position
        else:
            self.velocity = Vector(0, 0, 0)
            self.position = Vector(0, 0, 0)

    def __add__(self, other):
        if isinstance(other, float):
            return State(self.velocity + other, self.position + other)  # float
        elif other.velocity:
            return State(self.velocity + other.velocity, self.position + other.position)  # state
        else:
            raise ValueError('can\'t add')

    def __mul__(self, other):
        if isinstance(other, float):
            return State(self.velocity * other, self.position * other)  # float
        elif other.velocity:
            return State(self.velocity * other.velocity, self.position * other.position)  # state
        else:
            raise ValueError('can\'t mul')

    def __rmul__(self, other):
        if isinstance(other, float):
            return State(self.velocity * other, self.position * other)  # state
        else:
            raise ValueError('can\'t mul')

    def __str__(self):
        return f'vel = {self.velocity}  pos = {self.position}'