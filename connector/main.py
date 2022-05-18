import asyncio
import time

import websockets

from src.Drone import Drone
from src.DronePhysics import DronePhysics
from src.Vector import Vector
from src.ConnectService import ConnectService
from src.СonvertService import ConvertService
from src.DockerService.DockerService import runDocker


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
        drone.blastOff()
    time.sleep(6)


def main():
    async def server(websocket, path):
        number = 0
        while True:
            timeStamp1 = time.time_ns() // 1000000
            for drone in drones:
                lat, lon, alt = drone.getLLA()
                drone.state.position.setXYZ(*ConvertService.geodetic2enu(lat, lon, alt, lat0, lon0, alt0))  # TODO: hide

            data = []
            for i in drones:
                data.append(f'{i.state.position.x} {i.state.position.z} {i.state.position.y + 5} {int(i.connected)}')
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
                new_velocity = physics.construct_velocity_vector(drone)
                drone.velocity = new_velocity
            timeStamp2 = time.time_ns() // 1000000
            if timeStamp2 - timeStamp1 >= 0:
                await asyncio.sleep(1.0 / 60 - (timeStamp2 - timeStamp1) / 1000)

    # ---------------------------------------------------main------------------------------------------

    positionsList1 = [(59.86805732560133, 30.56717405661705), (59.86805732560371, 30.567188808769522),
                       (59.868057325604035, 30.567201549263782), (59.867993559987376, 30.56718404313254),
                       (59.867992213527096, 30.56719879526668), (59.86799288676702, 30.567170632097273)]

    targets1 = [Vector(-3, -10, 25), Vector(0, -10, 25), Vector(3, -10, 25),
               Vector(-3, 10, 25), Vector(0, 10, 25), Vector(3, 10, 25)]

    positionsListDuo = [(59.86805732560133, 30.56717405661705), (59.867993559987376, 30.56718404313254)]
    targetsDuo = [Vector(-3, -10, 25), Vector(-3, 10, 25)]

    positionsList2 = [(59.868012717193984, 30.567235680640323), (59.8680117073538, 30.5672497622265),
                      (59.86801170735036, 30.567263173261424), (59.868011707346014, 30.56727658429701)]

    targets2 = [Vector(60, 0, 25), Vector(61, 0, 25), Vector(62, 0, 25), Vector(63, 0, 25)]

    positionsList3 = [(59.86805109104228, 30.56719410639538), (59.86804301233604, 30.567192765297996),
                      (59.868036616695086, 30.567194106408866), (59.868042675726386, 30.567204835241206)]

    positionsList4 = [(59.8680204711637, 30.56717621212066), (59.86802754003335, 30.56719163482928),
                      (59.86801306567738, 30.567192975922822), (59.868019461323115, 30.56719163482339)]

    positionsList5 = [(59.94635532180626, 30.817165711747744), (59.94635389728687, 30.817721419704696),
                      (59.94610646277668, 30.817727107896264), (59.946110261889224, 30.817161921032508)]

    targets5 = [Vector(31.37696495, -27.72570174, 25),
                Vector(-0.21186666, -27.30256879, 25),
                Vector(1.16614274e-10, -4.74592809e-10, 25),
                Vector(31.05881508, -0.15857792, 25)]

    for i in positionsList2:
        print(ConvertService.geodetic2enu(i[0], i[1], 25, positionsList2[0][0], positionsList2[0][1], 0))
    # --- run Docker images ---
    runDocker(positionsList2)
    time.sleep(10) # нужно подождать, пока контейнеры разгрузятся

    vel_m_c = 1
    drones = createDrones(vel_m_c, targets2)
    lat0, lon0, alt0 = ConnectService.connectDrones(drones)

    climb(drones)
    physics = DronePhysics()

    start_server = websockets.serve(server, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    print('ready to connect')
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
