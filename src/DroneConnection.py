import argparse
from connector.geoscan_uav import UAV


class DroneConnection(UAV):
    def __init__(self, port: str):
        args = argparse.ArgumentParser()
        args.add_argument('--address', dest='address', help='server address and port X.X.X.X:X',
                          default=f'127.0.0.1:{port}')
        args.add_argument('--modem', dest='modem', help='modem socket', default='1:2')
        args.add_argument('--cache', dest='cache', help='component cache directory', default='/cache')
        options = args.parse_args()

        super().__init__(tcp=options.address, modem=options.modem, cache=options.cache)
