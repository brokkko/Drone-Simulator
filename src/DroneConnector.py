import argparse
from connector.geoscan_uav import UAV


class DroneConnector(UAV):
    startPort = 57981
    occupiedPorts = []

    def __init__(self):
        args = argparse.ArgumentParser()
        args.add_argument('--address', dest='address', help='server address and port X.X.X.X:X',
                          default=f'127.0.0.1:{self._getPortOfFreeContainer()}')
        args.add_argument('--modem', dest='modem', help='modem socket', default='1:2')
        args.add_argument('--cache', dest='cache', help='component cache directory', default='/cache')
        options = args.parse_args()

        super().__init__(tcp=options.address, modem=options.modem, cache=options.cache)

    @staticmethod
    def _getPortOfFreeContainer():
        if len(DroneConnector.occupiedPorts) == 0:
            DroneConnector.occupiedPorts.append(DroneConnector.startPort)
            # TODO: start container
            return str(DroneConnector.startPort)
        else:
            DroneConnector.occupiedPorts.append(DroneConnector.occupiedPorts[-1] + 1)
            # TODO: start container
            return str(DroneConnector.occupiedPorts[-1])
