import docker
import configparser
from typing import List


def runDocker(latlonList: List[tuple]) -> None:
    client = docker.from_env()
    for container in client.containers.list():
        container.stop()

    c = configparser.ConfigParser()
    c.read("DockerService/config.ini")
    config = c['docker']

    image = config['image_name']
    client = docker.from_env()

    for i, latlon in enumerate(latlonList):
        port = {'8000/tcp': int(config['start_port']) + i}  # container: host
        mount = {config['path'] + str(i): {'bind': '/usr/src/app/cache', 'mode': 'rw'}} # host : container
        env = [f'LAT={latlon[0]}', f'LON={latlon[1]}']
        name = image + str(i)
        client.containers.run(image, "./start.sh", ports=port, volumes=mount, environment=env, tty=True, auto_remove=True, name=name, detach= True)

