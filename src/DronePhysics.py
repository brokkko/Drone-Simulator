from src.Drone import Drone
from src.Vector import Vector


class DronePhysics:
    def __init__(self):
        self.k1 = 2.0
        self.k2 = 1.0
        self.k3 = 2.5
        self.h = 0.01
        
    def quadraticDependence(self, k: float) -> float:
        return k*k - 2*k + 1

    def localK3(self, drone1: Drone, drone2: Drone):
        if drone1.state.position.distance_to(drone2.state.position) <= drone1.critical_radius:
            return self.k3

        distBefore = drone1.state.position.distance_to(drone2.state.position)
        drone1After = drone1.state.position + (self.h * drone1.velocity)
        drone2After = drone2.state.position + (self.h * drone2.velocity)
        distAfter = drone1After.distance_to(drone2After)

        if distBefore - distAfter <= 0:
            return 0

        if drone1.velocity != Vector(0, 0, 0) and drone2.velocity != Vector(0, 0, 0):
            print(f"delta = {distBefore-distAfter}  max = {distBefore}")
            speed = (distBefore - distAfter) / (self.h*(drone1.velocity.length() + drone2.velocity.length()))
        else:
            speed = 0

        dist = (distBefore / drone1.safe_radius)
        quadro = self.quadraticDependence(dist)
        if speed < 0.2:
            k = quadro
        else:
            k = (quadro + speed)/2

        # if drone1.id == 3 or drone1.id == 4:
        print(f'{drone1.id} dist = {dist}  speed = {speed}  quadro = {quadro}  k = {k}')

        return k

    def countK3(self, drone: Drone):
        values = []
        for neighbor in drone.neighbors:
            if drone.state.position.distance_to(neighbor.state.position) <= drone.safe_radius:
                values.append(self.localK3(drone, neighbor))
        return max(values) if len(values) else 0

    def construct_velocity_vector(self, drone: Drone) -> Vector:

        if drone.connected == 0 or drone.connected == 2:
            return Vector()

        if drone.state.position.distance_to(drone.target) <= 1 and drone.connected:
            print(f'drone {drone.id} reached')
            drone.connected = 2
            return Vector()

        k3 = self.countK3(drone) * self.k3
        if k3 != 0:
            print("RESULT >>>> ", k3)
        # print("\n")

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
