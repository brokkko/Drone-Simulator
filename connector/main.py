import asyncio
import math
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


def init():
    drones = []
    for index in range(1, 7):
        drones.append(Drone(Vector(10, 50 * index, 50), Vector(7, 0, 0), Vector(500, 50 * index, 50), index, True))

    drones.append(Drone(Vector(250, 50 * 3, 50), Vector(0, 0, 0), Vector(500, 50 * 7, 30), 7, False))
    drones.append(Drone(Vector(220, 50 * 1, 48), Vector(0, 0, 0), Vector(500, 50 * 8, 30), 8, False))
    drones.append(Drone(Vector(380, 50 * 4 + 17, 52), Vector(0, 0, 0), Vector(500, 50 * 9, 30), 9, False))
    drones.append(Drone(Vector(250, 50 * 2, 50), Vector(0, 0, 0), Vector(500, 50 * 9, 0), 9, False))

    return drones


transformer = pyproj.Transformer.from_crs(
    {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
    {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
)


#def init_drone_connection():
args = argparse.ArgumentParser()
args.add_argument('--address', dest='address', help='server address and port X.X.X.X:X', default='127.0.0.1:57891')
args.add_argument('--modem', dest='modem', help='modem socket', default='1:2')
args.add_argument('--cache', dest='cache', help='component cache directory', default='/cache')
options = args.parse_args()

uav = UAV(tcp=options.address, modem=options.modem, cache=options.cache)
uav.connect()
time.sleep(3)
print("connected")
uav.control.preflight()
time.sleep(1)
print("preflighted")
uav.control.takeoff()
time.sleep(3)
print("takeoffed")
lat0, lon0, alt0 = int(uav.messenger.hub['Ublox']['latitude'].read()[0]), \
                   int(uav.messenger.hub['Ublox']['longitude'].read()[0]), \
                   int(uav.messenger.hub['Ublox']['altitude'].read()[0])

lat0, lon0, alt0 = lat0 / (10 ** 7), lon0 / (10 ** 7), alt0 / (10 ** 3)


async def main(websocket, path):
    # droneList = init()
    # addNeighbors(droneList)
    # physics = DronePhysics()
    # h = 0.15

    vel_mm_c = 1000
    north = 0
    east = 0
    down = vel_mm_c
    data = last = '0'

    while True:
        vel_mm_c = 1000
        north = 0
        east = 0
        down = 0

        # for index in range(len(droneList)):
        #     physics.rungeKutta(droneList[index], h)

        # str_to_send = []
        # for i in droneList:
        #     str_to_send.append(f'{i.state.position.x} {i.state.position.z} {i.state.position.y} {int(i.connected)}')
        # str_to_send = '|'.join(str_to_send)

        if data =='w':
            north = vel_mm_c
        elif data == 's':
            north = -vel_mm_c
        elif data == 'a':
            east = -vel_mm_c
        elif data == 'd':
            east = vel_mm_c
        elif data == 'q':
            down = -vel_mm_c

        lat, lon, alt = int(uav.messenger.hub['Ublox']['latitude'].read()[0]), \
                        int(uav.messenger.hub['Ublox']['longitude'].read()[0]), \
                        int(uav.messenger.hub['Ublox']['altitude'].read()[0])

        coord_list = geodetic2enu(lat / (10 ** 7), lon / (10 ** 7), alt / (10 ** 3), lat0, lon0, alt0)
        print(coord_list)

        drone.state.position.x = coord_list[0]
        drone.state.position.y = coord_list[1]
        drone.state.position.z = coord_list[2]

        if data != '0':
            # print(x1, y1, z1)
            # print("Drone: ", drone.state.position.x, drone.state.position.y, drone.state.position.z)
            uav.control.go_manual_22mode(north, east, down, 0, 1000)

        str_to_send = [f'{drone.state.position.x} {drone.state.position.z} {drone.state.position.y} {1}']
        str_to_send = '|'.join(str_to_send)

        await websocket.send(str_to_send)
        await asyncio.sleep(1.0 / 60)

        data = await websocket.recv()

start_server = websockets.serve(main, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print('ready to connect')
asyncio.get_event_loop().run_forever()

