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

    image = config['image_name']
    client = docker.from_env()

    # --env LAT=59.99234113142696 --env LON=30.280999708037204
    for i, latlon in enumerate(latlonList):
        # os.system(f"docker run -p {int(config['start_port']) + i}:8000"
        #           f" -v {config['path'] + str(i)}:/usr/src/app/cache"
        #           f" --env LAT={latlon[0]} --env LON={latlon[1]}"
        #           f" --name sim{i} -it --rm sim ./start.sh")
        # print('hi')

        port = {'8000/tcp': int(config['start_port']) + i}  # container: host
        mount = {config['path'] + str(i): {'bind': '/usr/src/app/cache', 'mode': 'rw'}} # host : container
        env = [f'LAT={latlon[0]}', f'LON={latlon[1]}']
        name = image + str(i)
        client.containers.run(image, "./start.sh", ports=port, volumes=mount, environment=env, tty=True, auto_remove=True, name=name, detach= True)
        print('hi')


if __name__ == '__main__':
    runDocker([('59.99234113142696', '30.280999708037204')])
