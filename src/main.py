from Vector import Vector
import asyncio
import websockets


async def hello(websocket, path):
    # name = await websocket.recv()
    # print("< {}".format(name))
    positions = Vector(200, 300, 7)
    # greeting = "Hello {}!".format(name)
    n = 10
    while n != 0:
        await websocket.send(f'{positions.get_xyz()}')
        positions.x += 10
        positions.y += 10
        positions.z += 10
        n -= 1
    # print("> {}".format(greeting))

start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



# if __name__ == "__main__":
#     sio = socketio.Server()
#     positions = Vector(200, 300, 7)
#     while True:
#         sio.emit('data', {'x': 200,
#                           'y': 300,
#                           'z': 7})
#         time.sleep(5)
