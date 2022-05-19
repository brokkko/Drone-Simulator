from src.Drone import Drone
from src.Vector import Vector
from typing import Final


def quadraticDependence(k: float) -> float:
    return k * k - 2 * k + 1


class DronePhysics:
    def __init__(self):
        self.k1: Final[float] = 2.0  # Target
        self.k2: Final[float] = 1.0  # Swarm movement
        self.k3: Final[float] = 2.5  # repulsion
        self.h: Final[float] = 0.01  # step for predicting approach
        self.approach: Final[float] = 0.2  # minimal approach of drones in one step
        self.targetAccuracy: Final[float] = 1

    def findLocalK3(self, drone1: Drone, drone2: Drone):
        # checking for critical distance of drones
        if drone1.position.distance_to(drone2.position) <= drone1.critical_radius:
            return self.k3

        distBefore = drone1.position.distance_to(drone2.position)
        drone1After = drone1.position + (self.h * drone1.velocity)
        drone2After = drone2.position + (self.h * drone2.velocity)
        distAfter = drone1After.distance_to(drone2After)

        if distBefore - distAfter <= 0:
            return 0

        # speed is taken into account only for moving drones
        if drone1.velocity != Vector(0, 0, 0) and drone2.velocity != Vector(0, 0, 0):
            speed = (distBefore - distAfter) / (self.h * (drone1.velocity.length() + drone2.velocity.length()))
        else:
            speed = 0

        normalizedDist = (distBefore / drone1.safeRadius)
        quadraticDist = quadraticDependence(normalizedDist)

        # if the approach of drones is less than 'approach', then the speed will not be taken into account
        if speed < self.approach:
            k = quadraticDist
        else:
            k = (quadraticDist + speed) / 2

        return k

    def countK3(self, drone: Drone):
        values = []
        for neighbor in drone.neighbors:
            if drone.position.distance_to(neighbor.position) <= drone.safeRadius:
                values.append(self.findLocalK3(drone, neighbor))
        return max(values) if len(values) else 0

    def constructVelocityVector(self, drone: Drone) -> Vector:
        # checking for unconnected drones
        if drone.connected == 0 or drone.connected == 2:
            return Vector()

        if drone.position.distance_to(drone.target) <= self.targetAccuracy and drone.connected:
            print(f'drone {drone.id} reached')
            drone.connected = 2  # status 2 means drone has reached his target
            return Vector()

        k3 = self.countK3(drone) * self.k3

        V_goal: Vector = self.k1 * (drone.target - drone.position) / (drone.target - drone.position).length()

        V_close: Vector = Vector()
        r_sum: Vector = Vector()
        for neighbour in drone.neighbors:
            if drone.position.distance_to(neighbour.position) <= drone.safeRadius:
                arg1: float = (neighbour.position - drone.position).length() / min(neighbour.position.length(),
                                                                                   drone.position.length())
                arg_goal = (neighbour.position - drone.position) / (neighbour.position - drone.position).length()
                r_dist = -k3 * ((2 - arg1) * (2 - arg1)) * arg_goal
                V_close += r_dist
                r_sum += neighbour.position

        V_swarm: Vector = Vector(0, 0, 0)
        if len(drone.neighbors) != 0:
            r_c = r_sum / (len(drone.neighbors))
            V_swarm: Vector = self.k2 * (r_c - drone.position) / (r_c - drone.position).length()

        # if there are no neighbors in the safety radius
        if r_sum == 0:
            V_close = Vector()

        return V_goal + V_close + V_swarm
