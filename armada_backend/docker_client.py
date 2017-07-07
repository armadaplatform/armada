import docker
from docker.types import HostConfig

from armada_command.scripts.compat import json
from armada_command.ship_config import get_ship_config

DOCKER_API_VERSION = '1.24'
DOCKER_SOCKET_PATH = '/var/run/docker.sock'


class DockerException(Exception):
    pass


def api(timeout=11):
    return docker.APIClient(base_url='unix://' + DOCKER_SOCKET_PATH, version=DOCKER_API_VERSION, timeout=timeout)


def _get_error_from_docker_pull_event(event):
    return event.get('error') or event.get('errorDetail')


def docker_pull(docker_api, dockyard_address, image_name, image_tag):
    image_address = dockyard_address + '/' + image_name
    pull_output = list(docker_api.pull(image_address, tag=image_tag,
                                       insecure_registry=True, stream=True))
    for event_json in pull_output:
        event = json.loads(event_json)
        error = _get_error_from_docker_pull_event(event)
        if error:
            raise DockerException('Cannot pull image {}:{}, error: {}'.format(image_address, image_tag, error))


def docker_tag(docker_api, dockyard_address, image_name, image_tag):
    image_address = dockyard_address + '/' + image_name
    tag_output = docker_api.tag(image_address, image_name, tag=image_tag)
    if not tag_output:
        raise DockerException('Cannot tag image {}:{}'.format(image_address, image_tag))


def create_host_config(docker_api, resource_limits, binds, port_bindings):
    resource_limits = resource_limits or {}
    privileged = get_ship_config().get('privileged', 'false').lower() == 'true'
    params = {
        'privileged': privileged,
        'publish_all_ports': True,
        'binds': binds,
        'port_bindings': port_bindings,
        'mem_limit': resource_limits.get('memory'),
        'memswap_limit': resource_limits.get('memory_swap'),
        'cgroup_parent': resource_limits.get('cgroup_parent'),
        'cpu_shares': resource_limits.get('cpu_shares'),
    }

    return HostConfig(DOCKER_API_VERSION, **params)
