from src.СonvertService import ConvertService
from src.Vector import Vector
import time


class ConnectService:

    @staticmethod
    def connectDrones(drones: []) -> Vector:
        for drone in drones:
            drone.connect()
        time.sleep(10)
        print("connected")

        for drone in drones:
            drone.uav.control.preflight()
        time.sleep(9)
        print("preflighted")
        for drone in drones:
            drone.uav.control.takeoff()
        time.sleep(18)

        print("took off")
        lat0, lon0, alt0 = drones[0].getLLA()

        for drone in drones:
            lat, lon, alt = drone.getLLA()
            drone.startPosition.setXYZ(*ConvertService.geodetic2enu(lat, lon, alt, lat0, lon0, alt0))
        return drones[0].getLLA()