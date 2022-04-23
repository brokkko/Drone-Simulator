import asyncio
import websockets
from src.Drone import Drone
from src.Vector import Vector
from src.DronePhysics import DronePhysics
import argparse
import time
from connector.geoscan_uav import UAV
# from pynput import keyboard
import keyboard
import pyproj
from pyproj import Proj


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
    # drones.append(Drone(Vector(250, 50 * 2 + 17 * 3, 0), Vector(0, 0, 0), Vector(500, 50 * 9, 0), 9))

    return drones


P = Proj(proj='utm',zone=10,ellps='WGS84', preserve_units=False)
G = pyproj.Geod(ellps='WGS84')


def latlon_to_xy(lat, lon):
    return P(lat, lon)


args = argparse.ArgumentParser()
args.add_argument('--address', dest='address', help='server address and port X.X.X.X:X', default='127.0.0.1:57891')
args.add_argument('--modem', dest='modem', help='modem socket', default='1:2')
args.add_argument('--cache', dest='cache', help='component cache directory', default='/cache')
options = args.parse_args()

uav = UAV(tcp=options.address, modem=options.modem, cache=options.cache)
uav.connect()
time.sleep(10)
print("connected")
uav.control.preflight()
time.sleep(1)
print("preflighted")
uav.control.takeoff()
time.sleep(13)
print("takeoffed")
x, y, z = int(uav.messenger.hub['Ublox']['latitude'].read()[0]), \
          int(uav.messenger.hub['Ublox']['longitude'].read()[0]), \
          int(uav.messenger.hub['Ublox']['altitude'].read()[0])
#
y0, x0 = P(y/(10**7), x/(10**7))
# print("Center: ", y0, x0)

drone = Drone(Vector(0, 0, 50), Vector(0, 0, 0), Vector(500, 500, 50), 1, False)
drone.neighbors = []


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
        down = vel_mm_c

        # for index in range(len(droneList)):
        #     physics.rungeKutta(droneList[index], h)

        # str_to_send = []
        # for i in droneList:
        #     str_to_send.append(f'{i.state.position.x} {i.state.position.z} {i.state.position.y} {int(i.connected)}')
        # str_to_send = '|'.join(str_to_send)

        if data =='w':
            # print("w PRESSED!!!")
            north = vel_mm_c
        elif data == 's':
            north = -vel_mm_c
        elif data == 'a':
            east = -vel_mm_c
        elif data == 'd':
            east = vel_mm_c
        elif data == 'q':
            down = -vel_mm_c

        x1, y1, z1 = int(uav.messenger.hub['Ublox']['latitude'].read()[0]), \
                     int(uav.messenger.hub['Ublox']['longitude'].read()[0]), \
                     int(uav.messenger.hub['Ublox']['altitude'].read()[0])
        # x1 = y1 = z1 = 0

        y1, x1 = P(y1/(10**7), x1/(10**7))
        #print("World position: ", y1, x1, z1/100)
        #print("Position on map: ", y1 - y0, x1 - x0, z1/100)
        drone.state.position.x = y1 - y0
        drone.state.position.y = x1-x0
        drone.state.position.z = z1/100 + 30
        if data != '0' and last != data:
            print("AAAAAAA: ", north, east, down)
            uav.control.go_manual_22mode(north, east, down, 0, 1000)
            # data = '0'

        str_to_send = [f'{drone.state.position.x} {drone.state.position.z} {drone.state.position.y} {1}']
        str_to_send = '|'.join(str_to_send)

        await websocket.send(str_to_send)
        await asyncio.sleep(1.0/60)
        last = data
        data = await websocket.recv()
        #print(data)

start_server = websockets.serve(main, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


# def on_press(key):
#     vel_mm_c = 1000
#     north = 0
#     east = 0
#     down = 0
#     try:
#         # print('Alphanumeric key pressed: {0} '.format(key.char))
#         if key.char == 'w':
#             north = vel_mm_c
#         elif key.char == 's':
#             north = -vel_mm_c
#         elif key.char == 'a':
#             east = -vel_mm_c
#         elif key.char == 'd':
#             east = vel_mm_c
#     except AttributeError:
#         # print('special key pressed: {0}'.format(key))
#         if key == keyboard.Key.up:
#             down = -vel_mm_c
#         elif key == keyboard.Key.down:
#             down = vel_mm_c
#     # print("Velocity: ", north, east, down)
#     x1, y1, z1 = int(uav.messenger.hub['Ublox']['latitude'].read()[0]), \
#                  int(uav.messenger.hub['Ublox']['longitude'].read()[0]), \
#                  int(uav.messenger.hub['Ublox']['altitude'].read()[0])
#
#     y1, x1 = P(y1/(10**7), x1/(10**7))
#     print("World position: ", y1, x1, z1/1000)
#     print("Position on map: ", y1 - y0, x1 - x0, z1/1000)
#     drone.state.position.x = y1 - y0
#     drone.state.position.y = x1-x0
#     uav.control.go_manual_22mode(north, east, down, 0, 1000)
#
#
# def on_release(key):
#     # print('Key released: {0}'.format(key))
#     if key == keyboard.Key.esc:
#         return False
#
#
# # Collect events until released
# listener = keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release)
# listener.start()
# listener.join()

