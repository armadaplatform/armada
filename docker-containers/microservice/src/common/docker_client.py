from __future__ import print_function

import docker

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


def api():
    return docker.Client(base_url='unix://' + DOCKER_SOCKET_PATH, version='1.15', timeout=7)
