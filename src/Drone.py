from typing import Tuple, Union, Any

from src.Vector import Vector
from src.State import State
from src.DroneConnector import DroneConnector


class Drone:
    def __init__(self, vel_m_c: int, target: Vector, drone_id: int, safe_radius: int, connected: bool):
        self.uav = DroneConnector()
        self.start_position = self.getPos()
        self.target = target
        self.maxSpeed = vel_m_c * 1000
        self.state = State(self.start_position)
        self.neighbors = []
        self.id = drone_id
        self.safe_radius = safe_radius
        self.connected = connected

    def getPos(self) -> Vector:
        lat, lon, alt = int(self.uav.messenger.hub['Ublox']['latitude'].read()[0]),\
                      int(self.uav.messenger.hub['Ublox']['longitude'].read()[0]),\
                      int(self.uav.messenger.hub['Ublox']['altitude'].read()[0])
        lat, lon, alt = lat / (10 ** 7), lon / (10 ** 7), alt / (10 ** 3)
        return lat, lon, alt

    def connect(self):
        self.uav.connect()

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
