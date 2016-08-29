import random
import time

from armada_backend import docker_client
from armada_backend.utils import deregister_services, shorten_container_id, get_container_parameters, get_ship_name
from armada_command.consul.consul import consul_query
from armada_command.consul import kv


def _get_local_services():
    all_services = consul_query('agent/services')
    del all_services['consul']
    return all_services


def _get_running_container_ids():
    docker_api = docker_client.api()
    return set(shorten_container_id(container['Id']) for container in docker_api.containers())

def _get_container_id_with_subservice(service_id):
    parts = service_id.split(":")
    container_id = parts[0]
    is_subservice = len(parts) > 1
    return container_id, is_subservice

def _mark_service_as_crashed(container_id, service_name):
    params = get_container_parameters(container_id)
    kv_index = 0
    if kv.kv_list('service/{}/'.format(service_name)):
        kv_index = int(kv.kv_list('service/{}/'.format(service_name))[-1].split('/')[2]) + 1
    kv.save_service(service_name, kv_index, 'crashed', params, container_id)


def _deregister_not_running_services():
    services = _get_local_services()
    running_containers_ids = _get_running_container_ids()
    for service_id in services.keys():
        container_id, is_subservice = _get_container_id_with_subservice(service_id)
        if container_id in running_containers_ids:
            continue
        if not is_subservice:
            _mark_service_as_crashed(container_id, services[service_id]['Service'])
        deregister_services(container_id)


def main():
    while True:
        _deregister_not_running_services()
        time.sleep(60 + random.uniform(-5, 5))


if __name__ == '__main__':
    main()
