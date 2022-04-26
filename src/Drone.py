from src.Vector import Vector
from src.State import State
from src.DroneConnection import DroneConnection


class Drone:
    def __init__(self, vel_m_c: int, target: Vector, id: int, safe_radius: int, connected: bool, port: str):
        self.uav = DroneConnection(port)
        self.start_position = self.getPos()
        self.target = target
        self.maxSpeed = vel_m_c
        self.state = State(Vector(50, 0, 0), self.start_position)
        self.neighbors = []
        self.id = id
        self.quality = None
        self.safe_radius = safe_radius
        self.connected = connected

    def getPos(self) -> Vector:
        lat, lon, alt = int(self.uav.messenger.hub['Ublox']['latitude'].read()[0]),\
                      int(self.uav.messenger.hub['Ublox']['longitude'].read()[0]),\
                      int(self.uav.messenger.hub['Ublox']['altitude'].read()[0])
        lat, lon, alt = lat / (10 ** 7), lon / (10 ** 7), alt / (10 ** 3)
        return Vector(lat, lon, alt)

    def connect(self):
        self.uav.connect()

    def update(self):  # TODO: clamp values min(clamp_max, max(clamp_min, value))
        self.uav.control.go_manual_22mode(self.state.velocity.x/1000, self.state.velocity.y/1000, self.state.velocity.z/1000, 0, 1000)

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
