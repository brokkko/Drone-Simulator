import Vector
from State import State


class Drone:

    def __init__(self, position: Vector, velocity: Vector, target: Vector, id: int):
        self.target = target
        self.state = State(velocity, position)
        self.neighbors = []
        self.id = id
        self.quality = None

    def __eq__(self, other):
        if other.target is None or other.state is None or other.neighbors is None:
            raise Exception('Drone undefined')
        return self.state == other.state and self.target == other.target and self.neighbors == other.neighbors

    def __ne__(self, other):
        if other.target is None or other.state is None or other.neighbors is None:
            raise Exception('Drone undefined')
        return self.state != other.state or self.target != other.target or self.neighbors != other.neighbors

    def __str__(self):
        return f'Drone {self.id} - {self.state}'



