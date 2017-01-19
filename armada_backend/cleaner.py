import random
import time

from armada_backend import docker_client
from armada_backend.utils import deregister_services, shorten_container_id, get_ship_ip, \
    get_ship_name, setup_sentry
from armada_command.consul import kv
from armada_command.consul.consul import consul_query


def _get_local_services():
    all_services = consul_query('agent/services')
    if 'consul' in all_services:
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


def _deregister_not_running_services():
    try:
        ship = get_ship_name()
    except:
        ship = get_ship_ip()
    services = _get_local_services()
    running_containers_ids = _get_running_container_ids()
    for service_id in services.keys():
        container_id, is_subservice = _get_container_id_with_subservice(service_id)
        if container_id in running_containers_ids:
            continue
        if not is_subservice:
            name = services[service_id]['Service']
            kv.update_container_status('crashed', ship=ship, name=name, container_id=container_id)
        deregister_services(container_id)

    all_valid_container_ids = set()
    all_valid_container_ids.update(running_containers_ids)

    services_keys = kv.kv_list('ships/{}/service/'.format(ship)) or []
    for service_key in services_keys:
        container_id = service_key.split('/')[-1]
        all_valid_container_ids.add(container_id)
        if container_id not in running_containers_ids:
            kv.update_container_status('crashed', key=service_key)
            deregister_services(container_id)

    _clean_up_kv_store(all_valid_container_ids)


def _clean_up_kv_store(all_valid_container_ids):
    start_timestamp_keys = kv.kv_list('start_timestamp/') or []
    for key in start_timestamp_keys:
        container_id = key.split('/')[-1]
        if container_id not in all_valid_container_ids:
            kv.kv_remove(key)

    is_single_instance_keys = kv.kv_list('is_single_instance/') or []
    for key in is_single_instance_keys:
        container_id = key.split('/')[-1].split(':')[0]
        if container_id not in all_valid_container_ids:
            kv.kv_remove(key)


def main():
    setup_sentry()
    while True:
        _deregister_not_running_services()
        time.sleep(60 + random.uniform(-5, 5))


if __name__ == '__main__':
    main()
