# Simple pygame program

# Import and initialize the pygame library
import pygame
import pygame.freetype
import time

from Drone import Drone
from Vector import Vector
from DronePhysics import DronePhysics

pygame.init()
pygame.font.init() # you have to call this at the start,

# Set up the drawing window
screen = pygame.display.set_mode([500, 500])



def addNeighbors(drones):
    for drone1 in drones:
        for drone2 in drones:
            if drone1 != drone2:
                drone1.neighbors.append(drone2)


def init():
    drones = []
    for index in range(1, 7):
        drones.append(Drone(Vector(10, 50 * index, 0), Vector(1, 0, 0), Vector(1000, 50 * index, 0), index))

    drones.append(Drone(Vector(250, 50 * 2, 0), Vector(0, 0, 0), Vector(1000, 50 * 7, 0), 7))
    drones.append(Drone(Vector(220, 50 * 1, 0), Vector(0, 0, 0), Vector(1000, 50 * 8, 0), 8))
    drones.append(Drone(Vector(250, 50 * 2 + 17, 0), Vector(0, 0, 0), Vector(1000, 50 * 9, 0), 9))
    drones.append(Drone(Vector(250, 50 * 2 + 17*2, 0), Vector(0, 0, 0), Vector(1000, 50 * 9, 0), 9))
    drones.append(Drone(Vector(250, 50 * 2 + 17*3, 0), Vector(0, 0, 0), Vector(1000, 50 * 9, 0), 9))

    return drones


def main():

    GAME_FONT = pygame.freetype.SysFont('Comic Sans MS', 12)

    droneList = init()
    addNeighbors(droneList)
    physics = DronePhysics()
    h = 0.15

    running = True
    while running:

        # for drone in droneList:
        #     if drone.id == 1:
        #         print(f"I am Drone {drone.id} with {drone}")
        #         for neighbour in drone.neighbors:
        #             print(neighbour)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with white
        screen.fill((255, 255, 255))

        for index in range(len(droneList)):
            physics.rungeKutta(droneList[index], h)
            pygame.draw.circle(screen, (0, 0, 255),
                               (droneList[index].state.position.x, droneList[index].state.position.y), 5)

            GAME_FONT.render_to(screen, (droneList[index].state.position.x - 6, droneList[index].state.position.y + 3), f"{droneList[index].quality}", (0,0,0))


        pygame.display.flip()


    pygame.quit()


if __name__ == "__main__":
    main()
