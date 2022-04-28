import asyncio
import websockets
from src.Drone import Drone
from src.DronePhysics import DronePhysics
from src.Vector import Vector
import time
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


def create_drones(vel_m_c, targets: []) -> []:
    drones = []
    safe_radius = 40
    drone_id = 1
    for target in targets:
        drones.append(Drone(vel_m_c, target, drone_id, safe_radius, True))
        drone_id += 1
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
    lat0, lon0, alt0 = drones[0].getLLA()

    for drone in drones:
        lat, lon, alt = drone.getLLA()
        drone.start_position.setXYZ(*geodetic2enu(lat, lon, alt, lat0, lon0, alt0))
    return drones[0].getLLA()


async def server(websocket, path):
    if len(DroneConnector.occupiedPorts) > 0:
        return

    print("hello")
    vel_m_c = 1
    targets = [Vector(0, 50, 50)] # [Vector(0, 0, 100)] #[Vector(50, 0, 20)]
    drones = create_drones(vel_m_c, targets)
    lat0, lon0, alt0 = init_drone_connection(drones)
    physics = DronePhysics()

    while True:
        for drone in drones:
            lat, lon, alt = drone.getLLA()
            drone.state.position.setXYZ(*geodetic2enu(lat, lon, alt, lat0, lon0, alt0))  # TODO: hide

        str_to_send = []
        for i in drones:
            str_to_send.append(f'{i.state.position.x} {i.state.position.z} {i.state.position.y} {int(i.connected)}')
        str_to_send = '|'.join(str_to_send)

        await websocket.send(str_to_send)
        await asyncio.sleep(1.0 / 60)

        for drone in drones:
            print(drone.state.position)
            new_velocity = physics.construct_velocity_vector(drone)
            # new_velocity = Vector(1, 0, 0)
            print(drone.id, ": ", new_velocity)
            # преобразовали
            drone.velocity = new_velocity
        print("---------------------------------")


start_server = websockets.serve(server, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print('ready to connect')
asyncio.get_event_loop().run_forever()
