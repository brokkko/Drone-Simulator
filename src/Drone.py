from typing import Tuple, Union, Any

from src.Vector import Vector
from src.DroneConnector import DroneConnector


class Drone:
    def __init__(self, vel_m_c: int, target: Vector, drone_id: int, safe_radius: float, connected: bool):
        self.uav = DroneConnector()
        self.startPosition = Vector()
        self._velocity = Vector()
        self.target = target
        self.maxSpeed = vel_m_c
        self.position = Vector()
        self.neighbors = []
        self.id = drone_id
        self.safeRadius = safe_radius
        self.criticalRadius = 0.20  # 20 см
        self.connected = connected  # 0 - Disconnected,  1 - on the way,  2 - reached

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, newVelocity: Vector):
        if newVelocity.length() > self.maxSpeed:
            newVelocity = (newVelocity / newVelocity.length()) * self.maxSpeed

        self._velocity = newVelocity.copy()
        newVelocity *= 50
        newVelocity.setXYZ(int(newVelocity.x), int(newVelocity.y), int(newVelocity.z))

        self.uav.control.go_manual_22mode(newVelocity.y, newVelocity.x, -newVelocity.z, 0, 1000)

    def getLLA(self) -> Tuple[Union[float, Any], Union[float, Any], Union[float, Any]]:
        lat, lon, alt = int(self.uav.messenger.hub['Ublox']['latitude'].read()[0]), \
                        int(self.uav.messenger.hub['Ublox']['longitude'].read()[0]), \
                        int(self.uav.messenger.hub['Ublox']['altitude'].read()[0])
        lat, lon, alt = lat / (10 ** 7), lon / (10 ** 7), alt / (10 ** 3)
        return lat, lon, alt

    def connect(self):
        self.uav.connect()

    def blastOff(self):
        self.uav.control.go_manual_22mode(0, 0, -1000, 0, 5000)

    def __str__(self):
        return f'Drone {self.id} - {self.position}'
