from src.Drone import Drone
from src.Vector import Vector


class DronePhysics:
    def __init__(self):
        self.k1 = 2.0
        self.k2 = 1.0
        self.k3 = 1.0
        self.h = 0.08
        
    def quadraticDependence(self, k: float) -> float:
        return k*k - 2*k + 1

    def localK3(self, drone1: Drone, drone2: Drone):
        distBefore = drone1.state.position.distance_to(drone2.state.position)
        drone1After = drone1.state.position + self.h * drone1.velocity
        drone2After = drone2.state.position + self.h * drone2.velocity
        distAfter = drone1After.distance_to(drone2After)

        if distBefore - distAfter <= 0:
            return 0

        return (drone1.safe_radius / distBefore) \
               * ((distBefore - distAfter) / (self.h * (drone1.velocity + drone2.velocity).length()))

    def countK3(self, drone: Drone):
        values = []
        for neighbor in drone.neighbors:
            values.append(self.localK3(drone, neighbor))
        return max(values)

    def construct_velocity_vector(self, drone: Drone) -> Vector:

        if drone.connected == 0 or drone.connected == 2:
            return Vector()

        if drone.state.position.distance_to(drone.target) <= 1 and drone.connected:
            print(f'drone {drone.id} reached')
            drone.connected = 2
            return Vector()

        k3 = self.countK3(drone) * self.k3
        print("RESULT >>>> ", k3)
        print("\n")

        # вектор достижения цели
        V_goal: Vector = self.k1 * (drone.target - drone.state.position) / (
                drone.target - drone.state.position).length()

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

                r_dist = -k3 * ((2 - arg1) * (2 - arg1)) * arg_goal
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
