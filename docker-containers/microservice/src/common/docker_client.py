from __future__ import print_function

import docker

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


def api():
    return docker.Client(base_url='unix://' + DOCKER_SOCKET_PATH, version='1.15', timeout=7)


def get_docker_inspect(container_id):
    docker_api = api()
    docker_inspect = docker_api.inspect_container(container_id)
    return docker_inspect
