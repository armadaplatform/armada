import json

import docker

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


class DockerException(Exception):
    pass


def api():
    return docker.Client(base_url='unix://' + DOCKER_SOCKET_PATH, version='1.15', timeout=7)


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
            raise DockerException('Cannot push image {}:{}, error: {}'.format(image_address, image_tag, error))
