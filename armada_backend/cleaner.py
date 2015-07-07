import random
import time

from armada_backend import docker_client
from armada_backend.api_run import LENGTH_OF_SHORT_CONTAINER_ID
from armada_backend.utils import deregister_services
from armada_command.consul.consul import consul_query


def get_local_services_ids():
    return consul_query('agent/services').keys()


def get_running_container_ids():
    docker_api = docker_client.api()
    return [container['Id'][:LENGTH_OF_SHORT_CONTAINER_ID] for container in docker_api.containers()]


def deregister_not_running_services():
    services_ids = get_local_services_ids()
    containers_ids = get_running_container_ids()
    for service_id in services_ids:
        if service_id != 'consul':
            container_id = service_id.split(':')[0]
            if container_id not in containers_ids:
                deregister_services(container_id)


def main():
    while True:
        deregister_not_running_services()
        time.sleep(60 + random.uniform(-5, 5))


if __name__ == '__main__':
    main()
