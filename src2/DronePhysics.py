import math
from typing import Type

import copy
from Drone import Drone
from State import State
from Vector import Vector
from src2.State import State


class DronePhysics:

    def quality(self, drone: Drone, next_velocity: Vector, h: float) -> float:
        if drone.state.velocity.length() == 0:
            return .0

        h*=3

        # f = Ttarget + Tclose
        Ttarget = ((drone.target.distance_to(drone.state.position))
                    - (drone.target.distance_to(drone.state.position + next_velocity * h))) / (next_velocity * h).length()

        radius = 50
        next_closest = current_closest = radius * radius
        for neighbour in drone.neighbors:
            if drone.state.position.distance_to(neighbour.state.position) <= radius:
                nextDist = neighbour.state.position.distance_to(drone.state.position + next_velocity * h)
                currentDist = neighbour.state.position.distance_to(drone.state.position)
                if next_closest > nextDist:
                    next_closest = nextDist
                    current_closest = currentDist

        if next_closest == current_closest == radius * radius:
            Tclose = 0
        else:
            Tclose = (next_closest - current_closest) / (next_velocity*h).length()

        # if next_closest < radius:
        #     # TODO: problem
        #     # print(f"PROBLEM DRONE: {drone}")
        #     return .0



        # print(f"Drone {drone.id}: Ttarget({Ttarget}) and Tclose({Tclose})")
        # print(Tclose)

        return Ttarget + Tclose

    def pathDefinition(self, drone: Drone, h: float) -> Vector:
        # здесь перебираем вектора, выбираем наилучший
        angle = math.radians(20)

        v: Vector = Vector(drone.state.velocity.x, drone.state.velocity.y, drone.state.velocity.z)
        v.rotate_z(-5*angle)

        pBest = Vector(0, 0, 0)
        best = 0
        # print("_-__________________")
        for i in range(1, 19):
            current = self.quality(drone, v.rotate_z(angle), h)
            #print(f'hereeee -------------{v}')
            #print(current)
            if current > best:
                best = current
                pBest = Vector(v.x, v.y, v.z)
        #if best == 0 and pBest == Vector(0, 0, 0):

        drone.quality = round(best, 3)
        return pBest

    def Fdt(self, drone: Drone, h: float) -> State:
        dX = State()
        # print(f"Before: {drone.state.position}")
        # dX.velocity = self.pathDefinition(drone, h) - drone.state.velocity
        # print(dX.velocity) self.pathDefinition(drone, h)
        # dX.velocity =  - drone.state.velocity #self.pathDefinition(drone, h)
        dX.position = self.pathDefinition(drone, h) # - drone.state.velocity
        # dX.velocity = Vector(drone.state.velocity.x,0,0)
        # print(f"After: {dX.position}")
        # dX.position = drone.state.velocity
        return dX

    def rungeKutta(self, drone: Drone, h: float):
        xdt = self.Fdt(drone, h)
        b = drone.state.velocity.length()
        drone.state = drone.state + (h * xdt)
        a = drone.state.velocity.length()
        # print(f'change in speed{b - a}')
        # print(drone.state.velocity)
        return drone
