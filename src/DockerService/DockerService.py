import docker
import os
import configparser

from typing import List


def runDocker(latlonList: List[tuple]) -> None:
    client = docker.from_env()
    for container in client.containers.list():
        container.stop()

    c = configparser.ConfigParser()
    c.read("config.ini")
    config = c['docker']

    # --env LAT=59.99234113142696 --env LON=30.280999708037204
    for i, latlon in enumerate(latlonList):
        os.system(f"docker create -p {int(config['start_port']) + i}:8000"
                  f" -v {config['path'] + str(i)}:/usr/src/app/cache"
                  f" --env LAT={latlon[0]} --env LON={latlon[1]}"
                  f" --name sim{i} --rm sim ./start.sh")


if __name__ == '__main__':
    runDocker([('59.99234113142696', '30.280999708037204')])
