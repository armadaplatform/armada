import docker

from armada_command.scripts.compat import json

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


class DockerException(Exception):
    pass


def api(timeout=11):
    return docker.Client(base_url='unix://' + DOCKER_SOCKET_PATH, version='1.18', timeout=timeout)


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
