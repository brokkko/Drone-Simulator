import argparse
import time
from geoscan_uav import UAV
from pynput import keyboard


args = argparse.ArgumentParser()
args.add_argument('--address', dest='address', help='server address and port X.X.X.X:X', default='127.0.0.1:8000')
args.add_argument('--modem', dest='modem', help='modem socket', default='1:2')
args.add_argument('--cache', dest='cache', help='component cache directory', default='cache')
options = args.parse_args()

uav = UAV(tcp = options.address, modem = options.modem, cache = options.cache)
uav.connect()
time.sleep(2)
print("connected")
uav.control.preflight()
time.sleep(1)
print("preflighted")
uav.control.takeoff()
time.sleep(2)
print("took off")
x = uav.messenger.hub['Ublox']
print(x)


def on_press(key):
	vel_mm_c = 1000
	north = 0
	east = 0
	down = 0
	try:
		print('Alphanumeric key pressed: {0} '.format(key.char))
		if key.char == 'w':
			north = vel_mm_c
		elif key.char == 's':
			north = -vel_mm_c
		elif key.char == 'a':
			east = -vel_mm_c
		elif key.char == 'd':
			east = vel_mm_c
	except AttributeError:
		print('special key pressed: {0}'.format(key))
		if key == keyboard.Key.up:
			down = -vel_mm_c
		elif key == keyboard.Key.down:
			down = vel_mm_c
	uav.control.go_manual_22mode(north,east,down,0,1000)

def on_release(key):
	print('Key released: {0}'.format(key))
	if key == keyboard.Key.esc:
		return False

# Collect events until released
# listener = keyboard.Listener(
#         on_press=on_press,
#         on_release=on_release)
# listener.start()
# listener.join()
