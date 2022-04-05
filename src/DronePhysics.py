import math
from typing import Type
import pygame

from Drone import Drone
from State import State
from Vector import Vector
from src.State import State


class DronePhysics:

    def __init__(self, screen=None, font=None):
        self.screen = screen
        self.font = font

    def construct_velocity_vector(self, drone: Drone) -> Vector:
        # or ((drone.state.position.x - drone.target.x) <= 0.01 and
        #     (drone.state.position.y - drone.target.y) <= 0.01 and
        #     (drone.state.position.z - drone.target.z) <= 0.01)
        if drone.state.velocity.x == 0 and drone.state.velocity.y == 0 and drone.state.velocity.z == 0:
            return Vector(0, 0, 0)
        k1 = 5.0
        k2 = 1.0
        k3 = 1.0
        radius = 40
        V_goal: Vector = k1 * (drone.target - drone.state.position) / (drone.target - drone.state.position).length()
        # вектор отталкивания
        V_close: Vector = Vector(0, 0, 0)
        r_sum: Vector = Vector(0, 0, 0)
        sum = 0
        for neighbour in drone.neighbors:
            arg1: float = (neighbour.state.position - drone.state.position).length() \
                          / min(neighbour.state.position.length(), drone.state.position.length())
            arg_goal = (neighbour.state.position - drone.state.position) \
                       / (neighbour.state.position - drone.state.position).length()
            r_dist = -k3 * ((2 - arg1) * (2 - arg1)) * arg_goal
            V_close += r_dist

            sum += 1
            if drone.state.position.distance_to(neighbour.state.position) <= radius:
                r_sum += neighbour.state.position

        r_c = r_sum / (sum + 1)
        V_center: Vector = k2 * (r_c - drone.state.position) / (r_c - drone.state.position).length()

        if r_sum.x == 0 and r_sum.y == 0 and r_sum.z == 0:
            V_close = Vector(0, 0, 0)

        return V_goal + V_close + V_center

    def quality(self, drone: Drone, next_velocity: Vector, h: float) -> float:
        if drone.state.velocity.length() == 0:
            return .0

        #h *= 3

        # f = Ttarget + Tclose
        Ttarget = ((drone.target.distance_to(drone.state.position))
                   - (drone.target.distance_to(drone.state.position + next_velocity * h))) / (
                          next_velocity * h).length()

        radius = 50
        count = 0
        # TODO: попробовать суммировать всех, кто находится в этом радиусе
        next_closest = current_closest = 0
        for neighbour in drone.neighbors:
            if drone.state.position.distance_to(neighbour.state.position) <= radius:
                nextDist = neighbour.state.position.distance_to(drone.state.position + next_velocity * h)
                currentDist = neighbour.state.position.distance_to(drone.state.position)
                # if next_closest > nextDist:
                next_closest += nextDist
                current_closest += currentDist
                count += 1

        if next_closest == current_closest == 0:
            Tclose = 0
        else:
            # Tclose = (next_closest/count - current_closest/count) / (next_velocity*h).length()
            # print(count)
            # print(next_closest/(count*radius))
            Tclose = (next_closest / (count * radius))
            #Tclose = 0

        # if next_closest < radius:
        #     # TODO: problem
        #     # print(f"PROBLEM DRONE: {drone}")
        #     return .0
        # if Tclose != 0:
        #     print(f"Drone {drone.id}: {Ttarget + Tclose}")
        # print(Tclose)

        return Ttarget + Tclose

    def pathDefinition(self, drone: Drone, h: float) -> Vector:
        # здесь перебираем вектора, выбираем наилучший
        angle = math.radians(25)

        v: Vector = Vector(drone.state.velocity.x, drone.state.velocity.y, drone.state.velocity.z)
        v.rotate_z(-4 * angle)

        pBest = Vector(0, 0, 0)
        best = 0
        # print("_-__________________")
        for i in range(1, 10):
            current = self.quality(drone, v.rotate_z(angle), h)

            # ----DEBUG
            if self.screen:
                v_end = drone.state.position + v * 100

                # pygame.draw.aaline(self.screen, (0, 0, 0), drone.state.position.get_xy(),
                #                    (drone.state.position + v * 100).get_xy())
                # print(v_end.get_xy())
                # self.font.render_to(self.screen, v_end.get_xy(), f"{round(current)}", (0, 0, 0))
            # ----DEBUG

            # print(f'hereeee -------------{v}')
            # print(current)
            if current > best:
                best = current
                pBest = Vector(v.x, v.y, v.z)
        # if best == 0 and pBest == Vector(0, 0, 0):

        drone.quality = round(best, 3)
        return pBest

    def Fdt(self, drone: Drone, h: float) -> State:
        dX = State()

        # dX.position = self.pathDefinition(drone, h)  # - drone.state.velocity
        dX.position = self.construct_velocity_vector(drone)

        return dX

    def rungeKutta(self, drone: Drone, h: float):
        xdt = self.Fdt(drone, h)
        b = drone.state.velocity.length()
        drone.state = drone.state + (h * xdt)
        a = drone.state.velocity.length()
        # print(f'change in speed{b - a}')
        # print(drone.state.velocity)
        return drone