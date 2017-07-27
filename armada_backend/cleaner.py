import random
import time

from armada_backend import docker_client
from armada_backend.models.services import get_local_services, update_container_status
from armada_backend.utils import deregister_services, shorten_container_id, setup_sentry, get_logger
from armada_backend.models.ships import get_ship_ip, get_ship_name
from armada_command import armada_api
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
            update_container_status('crashed', ship=ship, service_name=name, container_id=container_id)
        deregister_services(container_id)

    for service_key in get_local_services():
        container_id = service_key.split('/')[-1]
        if container_id not in running_containers_ids:
            update_container_status('crashed', key=service_key)
            deregister_services(container_id)


def get_next_kv_clean_up_timestamp():
    return time.time() + random.randint(30 * 60, 60 * 60)


next_kv_clean_up_timestamp = get_next_kv_clean_up_timestamp()


def _clean_up_kv_store():
    global next_kv_clean_up_timestamp
    if time.time() < next_kv_clean_up_timestamp:
        return
    get_logger().info('Cleaning up kv-store:')
    next_kv_clean_up_timestamp = get_next_kv_clean_up_timestamp()

    services = armada_api.get_json('list')
    valid_container_ids = set(service.get('container_id') for service in services)

    start_timestamp_keys = kv.kv_list('start_timestamp/') or []
    for key in start_timestamp_keys:
        container_id = key.split('/')[-1]
        if container_id not in valid_container_ids:
            get_logger().info('Removing key: {}'.format(key))
            kv.kv_remove(key)

    single_active_instance_keys = kv.kv_list('single_active_instance/') or []
    for key in single_active_instance_keys:
        container_id = key.split('/')[-1].split(':')[0]
        if container_id not in valid_container_ids:
            get_logger().info('Removing key: {}'.format(key))
            kv.kv_remove(key)
    get_logger().info('Finished cleaning up kv-store.')


def main():
    setup_sentry()
    while True:
        _deregister_not_running_services()
        _clean_up_kv_store()
        time.sleep(60 + random.uniform(-5, 5))


if __name__ == '__main__':
    main()
