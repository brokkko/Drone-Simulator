import asyncio
import websockets
from Drone import Drone
from Vector import Vector
from DronePhysics import DronePhysics


def addNeighbors(drones):
    for drone1 in drones:
        for drone2 in drones:
            if drone1 != drone2:
                drone1.neighbors.append(drone2)


def init():
    drones = []
    for index in range(1, 7):
        drones.append(Drone(Vector(10, 50 * index, 0), Vector(7, 0, 0), Vector(500, 50 * index, 0), index))

    drones.append(Drone(Vector(250, 50 * 2, 0), Vector(0, 0, 0), Vector(500, 50 * 7, 0), 7))
    drones.append(Drone(Vector(220, 50 * 1, 0), Vector(0, 0, 0), Vector(500, 50 * 8, 0), 8))
    # drones.append(Drone(Vector(250, 50 * 2 + 17, 0), Vector(0, 0, 0), Vector(500, 50 * 9, 0), 9))
    # drones.append(Drone(Vector(250, 50 * 2 + 17 * 2, 0), Vector(0, 0, 0), Vector(500, 50 * 9, 0), 9))
    # drones.append(Drone(Vector(250, 50 * 2 + 17 * 3, 0), Vector(0, 0, 0), Vector(500, 50 * 9, 0), 9))

    return drones


async def main(websocket, path):

    droneList = init()
    addNeighbors(droneList)
    physics = DronePhysics()
    h = 0.015

    while True:
        for index in range(len(droneList)):
            physics.rungeKutta(droneList[index], h)

        str_to_send = []
        for i in droneList:
            str_to_send.append(f'{i.state.position.x} {i.state.position.z} {i.state.position.y}')
        str_to_send = '|'.join(str_to_send)

        await websocket.send(str_to_send)

start_server = websockets.serve(main, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
