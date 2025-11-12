import socket

import docker

DOCKER_API_VERSION = '1.44'
DOCKER_SOCKET_PATH = '/var/run/docker.sock'


def api():
    return docker.APIClient(base_url='unix://' + DOCKER_SOCKET_PATH, version=DOCKER_API_VERSION, timeout=7)


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
        network_settings = docker_inspect['NetworkSettings']
        
        # Docker API >= 1.44: Gateway is in Networks
        if 'Networks' in network_settings and network_settings['Networks']:
            # Get first network's gateway
            first_network = list(network_settings['Networks'].values())[0]
            gateway_ip = first_network.get('Gateway')
        else:
            # Fallback for older Docker API versions
            gateway_ip = network_settings.get('Gateway')
        
        if not gateway_ip:
            raise Exception("Could not determine gateway IP from Docker inspect")
            
        _SHIP_IP = gateway_ip
    return _SHIP_IP
