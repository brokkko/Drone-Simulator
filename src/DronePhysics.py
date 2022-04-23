import math
from src.Drone import Drone
from src.Vector import Vector
from src.State import State


class DronePhysics:

    def construct_velocity_vector(self, drone: Drone) -> Vector:
        if (drone.state.velocity.x == 0 and drone.state.velocity.y == 0 and drone.state.velocity.z == 0) or \
                drone.state.position.distance_to(drone.target) <= 0.1:
            return Vector(0, 0, 0)
        k1 = 5.0
        k2 = 1.0
        k3 = 2.0
        V_goal: Vector = k1 * (drone.target - drone.state.position) / (drone.target - drone.state.position).length()
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

        r_c = r_sum / (sum + 1)
        V_center: Vector = k2 * (r_c - drone.state.position) / (r_c - drone.state.position).length()

        if r_sum.x == 0 and r_sum.y == 0 and r_sum.z == 0:
            V_close = Vector(0, 0, 0)

        return V_goal + V_close + V_center

    def quality(self, drone: Drone, next_velocity: Vector, h: float) -> float:
        if drone.state.velocity.length() == 0:
            return .0

        h *= 3

        # f = Ttarget + Tclose
        Ttarget = ((drone.target.distance_to(drone.state.position))
                   - (drone.target.distance_to(drone.state.position + next_velocity * h))) / (
                          next_velocity * h).length()

        radius = 60
        next_closest = current_closest = -1
        sum = 0
        for neighbour in drone.neighbors:
            if drone.state.position.distance_to(neighbour.state.position) <= radius:
                # if drone.id not in range(8, 10):
                #     print("here ", neighbour.id)
                sum += 1
                nextDist = neighbour.state.position.distance_to(drone.state.position + next_velocity * h)
                currentDist = neighbour.state.position.distance_to(drone.state.position)
                if next_closest > nextDist or next_closest == -1:
                    next_closest = nextDist
                    current_closest = currentDist

        # if drone.id not in range(8, 10) and sum > 0:
        #     # print(next_closest)
        if next_closest == current_closest == -1:
            Tclose = 0
        else:
            Tclose = (next_closest - current_closest) / (next_velocity * h).length()
            # print(Tclose)

        # if next_closest < radius:
        #     # TODO: problem
        #     # print(f"PROBLEM DRONE: {drone}")
        #     return .0
        # if Tclose != 0:
        #     print(f"Drone {drone.id}: {Ttarget + Tclose}")
        # print(Tclose)

        return Ttarget + 1 * Tclose

    def pathDefinition(self, drone: Drone, h: float) -> Vector:
        # здесь перебираем вектора, выбираем наилучший
        angle = math.radians(25)

        v: Vector = Vector(drone.state.velocity.x, drone.state.velocity.y, drone.state.velocity.z)
        v.rotate_z(-8 * angle)

        pBest = Vector(0, 0, 0)
        best = 0

        for i in range(1, 19):
            current = self.quality(drone, v.rotate_z(angle), h)

            if current > best:
                best = current
                pBest = Vector(v.x, v.y, v.z)

        return pBest

    def Fdt(self, drone: Drone, h: float) -> State:
        dX = State()

        dX.velocity = self.construct_velocity_vector(drone)  # - drone.state.velocity
        dX.position = dX.velocity
        # dX.position = self.pathDefinition(drone, h)

        return dX

    def rungeKutta(self, drone: Drone, h: float):
        xdt = self.Fdt(drone, h)
        drone.state = drone.state + (h * xdt)
        return drone
