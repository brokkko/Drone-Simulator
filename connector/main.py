import asyncio
import time
import websockets

from src.Drone import Drone
from src.DronePhysics import DronePhysics
from src.ConnectService import ConnectService
from src.СonvertService import ConvertService
from src.DockerService.DockerService import runDocker
from src.TestData import getTestData


def addNeighbors(drones):
    for drone1 in drones:
        for drone2 in drones:
            if drone1 != drone2:
                drone1.neighbors.append(drone2)


def createDrones(vel_m_c, targets: []) -> []:
    drones = []
    safe_radius = 5
    drone_id = 1
    for target in targets:
        drones.append(Drone(vel_m_c, target, drone_id, safe_radius, True))
        drone_id += 1
    addNeighbors(drones)
    return drones


def climb(drones: []):
    for drone in drones:
        drone.  blastOff()
    time.sleep(6)


def main():
    async def server(websocket, path):
        number = 0
        while True:
            timeStamp1 = time.time_ns() // 1000000
            for drone in drones:
                lat, lon, alt = drone.getLLA()
                drone.position.setXYZ(*ConvertService.geodetic2enu(lat, lon, alt, lat0, lon0, alt0))

            data = []
            for i in drones:
                data.append(f'{i.position.x} {i.position.z} {i.position.y + 5} {int(i.connected)}')
            data = '|'.join(data)
            number += 1

            await websocket.send(data)

            drone_id = int(await websocket.recv())
            if drone_id != -1:
                print(f"change{drone_id}")
            if drone_id != -1 and len(drones) >= drone_id + 1:
                if drones[int(drone_id)].connected != 2:
                    drones[int(drone_id)].connected = not drones[int(drone_id)].connected

            for drone in drones:
                new_velocity = physics.constructVelocityVector(drone)
                drone.velocity = new_velocity
            timeStamp2 = time.time_ns() // 1000000
            if timeStamp2 - timeStamp1 >= 0:
                await asyncio.sleep(1.0 / 60 - (timeStamp2 - timeStamp1) / 1000)

    # ---------------------------------------------------main------------------------------------------
    testNumber = 4
    testPositions, testTargets = getTestData(testNumber)
    # --- run Docker images ---
    runDocker(testPositions)
    time.sleep(10)  # waiting for containers to load

    vel_m_c = 1
    drones = createDrones(vel_m_c, testTargets)
    lat0, lon0, alt0 = ConnectService.connectDrones(drones)
    climb(drones)
    physics = DronePhysics()

    start_server = websockets.serve(server, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    print('ready to connect')
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
