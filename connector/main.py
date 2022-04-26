import asyncio
import websockets
from src.Drone import Drone
from src.Vector import Vector
from src.DronePhysics import DronePhysics
import argparse
import time
from connector.geoscan_uav import UAV
import numpy as np
import pyproj
import scipy.spatial.transform


def addNeighbors(drones):
    for drone1 in drones:
        for drone2 in drones:
            if drone1 != drone2:
                drone1.neighbors.append(drone2)


def geodetic2enu(lat, lon, alt, lat_org, lon_org, alt_org):
    transformer = pyproj.Transformer.from_crs(
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
    )
    x, y, z = transformer.transform(lon, lat, alt, radians=False)
    x_org, y_org, z_org = transformer.transform(lon_org, lat_org, alt_org, radians=False)
    vec = np.array([[x - x_org, y - y_org, z - z_org]]).T

    rot1 = scipy.spatial.transform.Rotation.from_euler('x', -(90 - lat_org),
                                                       degrees=True).as_matrix()  # angle*-1 : left handed *-1
    rot3 = scipy.spatial.transform.Rotation.from_euler('z', -(90 + lon_org),
                                                       degrees=True).as_matrix()  # angle*-1 : left handed *-1

    rotation_matrix = rot1.dot(rot3)

    enu = rotation_matrix.dot(vec).T.ravel()
    return enu.T


def create_drones(ports: [], vel_m_c) -> []:
    drones = []
    safe_radius = 40
    id = 1
    for port in ports:
        drones.append(Drone(vel_m_c, Vector(500, 500, 50), id, safe_radius, True, port))
        id += 1
    addNeighbors(drones)
    return drones


def init_drone_connection(drones: []) -> Vector:
    for drone in drones:
        drone.connect()
    time.sleep(3)
    print("connected")
    for drone in drones:
        drone.uav.control.preflight()
    time.sleep(1)
    print("preflighted")
    for drone in drones:
        drone.uav.control.takeoff()
    time.sleep(13)
    print("took off")
    return drones[0].getPos()


async def server(websocket, path):
    ports = ["57891"]
    vel_m_c = 1
    drones = create_drones(ports, vel_m_c)
    lat0, lon0, alt0 = init_drone_connection(drones)

    while True:
        for drone in drones:
            drone.update()

        str_to_send = []
        for i in drones:
            str_to_send.append(f'{i.state.position.x} {i.state.position.z} {i.state.position.y} {int(i.connected)}')
        str_to_send = '|'.join(str_to_send)

        await websocket.send(str_to_send)
        await asyncio.sleep(1.0 / 60)


start_server = websockets.serve(server, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print('ready to connect')
asyncio.get_event_loop().run_forever()

