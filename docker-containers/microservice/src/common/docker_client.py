from __future__ import print_function

import socket

import docker

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


def api():
    return docker.Client(base_url='unix://' + DOCKER_SOCKET_PATH, version='1.15', timeout=7)


def get_docker_inspect(container_id):
    docker_api = api()
    docker_inspect = docker_api.inspect_container(container_id)
    return docker_inspect


_SHIP_IP = None


def get_ship_ip():
    global _SHIP_IP
    if _SHIP_IP is None:
        container_id = socket.gethostname()
        docker_inspect = get_docker_inspect(container_id)
        gateway_ip = docker_inspect['NetworkSettings']['Gateway']
        _SHIP_IP = gateway_ip
    return _SHIP_IP
