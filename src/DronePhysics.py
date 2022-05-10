from src.Drone import Drone
from src.Vector import Vector


class DronePhysics:
    def __init__(self):
        self.k1 = 2.0
        self.k2 = 1.0
        self.k3 = 3.0

    def construct_velocity_vector(self, drone: Drone) -> Vector:
        if drone.connected == 0 or drone.connected == 2:
            return Vector()

        if drone.state.position.distance_to(drone.target) <= 1 and drone.connected:
            print(f'drone {drone.id} reached')
            drone.connected = 2
            return Vector()

        # вектор достижения цели
        V_goal: Vector = self.k1 * (drone.target - drone.state.position) / (drone.target - drone.state.position).length()

        # вектор отталкивания
        V_close: Vector = Vector(0, 0, 0)
        r_sum: Vector = Vector(0, 0, 0)
        sum = 0
        for neighbour in drone.neighbors:
            if drone.state.position.distance_to(neighbour.state.position) <= drone.safe_radius:
                arg1: float = (neighbour.state.position - drone.state.position).length() \
                              / min(neighbour.state.position.length(), drone.state.position.length())
                arg_goal = (neighbour.state.position - drone.state.position) \
                           / (neighbour.state.position - drone.state.position).length()

                r_dist = -self.k3 * ((2 - arg1) * (2 - arg1)) * arg_goal
                V_close += r_dist

            sum += 1
            r_sum += neighbour.state.position

        # вектор движения в рое
        V_center: Vector = Vector(0, 0, 0)
        if len(drone.neighbors) != 0:
            r_c = r_sum / (sum + 1)
            V_center: Vector = self.k2 * (r_c - drone.state.position) / (r_c - drone.state.position).length()

        if r_sum.x == 0 and r_sum.y == 0 and r_sum.z == 0:
            V_close = Vector(0, 0, 0)

        return V_goal + V_close + V_center

