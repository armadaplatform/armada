import argparse
import os
import sys
from collections import Counter
from time import sleep
from uuid import uuid4

from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.utils import get_logger, get_ship_name, shorten_container_id, setup_sentry
from armada_command import armada_api
from armada_command.consul import kv
from armada_command.consul.consul import consul_query
from armada_command.scripts.compat import json

RECOVERY_COMPLETED_PATH = '/tmp/recovery_completed'
RECOVERY_RETRY_LIMIT = 5
DELAY_BETWEEN_RECOVER_RETRY_SECONDS = 18


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('saved_containers_path')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    return parser.parse_args()


def _load_saved_containers_parameters_list(running_containers_parameters_path):
    with open(running_containers_parameters_path) as f:
        return json.load(f)


def _get_local_running_containers():
    result = []
    ship = get_ship_name()
    local_containers = kv.kv_list('ships/{}/service/'.format(ship)) or []
    for container in local_containers:
        container_parameters = kv.kv_get(container)['params']
        if container_parameters:
            result.append(container_parameters)
    return result


def _recover_container(container_parameters):
    get_logger().info('Recovering: %s ...\n', json.dumps(container_parameters))
    recovery_result = armada_api.post('run', container_parameters)
    if recovery_result.get('status') == 'ok':
        get_logger().info('Recovered container: %s', json.dumps(recovery_result))
        return True
    else:
        get_logger().error('Could not recover container: %s', json.dumps(recovery_result))
        return False


def _multiset_difference(a, b):
    a_counter = Counter(json.dumps(x, sort_keys=True) for x in a)
    b_counter = Counter(json.dumps(x, sort_keys=True) for x in b)
    difference = a_counter - b_counter
    return [json.loads(x) for x in difference.elements()]


def _load_from_dict(saved_containers, ship):
    saved_containers_list = [saved_container['params'] for saved_container in saved_containers.values()]
    _load_from_list(saved_containers_list, ship)


def _load_from_list(saved_containers, ship):
    wait_for_consul_ready()
    running_containers = _get_local_running_containers()
    containers_to_be_added = _multiset_difference(saved_containers, running_containers)
    for container_parameters in containers_to_be_added:
        get_logger().info('Added service: {}'.format(container_parameters))
        kv.save_container(ship, _generate_id(), 'crashed', params=container_parameters)


def _load_containers_to_kv_store(saved_containers_path):
    wait_for_consul_ready()
    try:
        ship = get_ship_name()
        saved_containers = _load_saved_containers_parameters_list(saved_containers_path)
        if isinstance(saved_containers, dict):
            _load_from_dict(saved_containers, ship)
        else:
            _load_from_list(saved_containers, ship)
    except:
        get_logger().exception('Unable to load from %s', saved_containers_path)


def _generate_id():
    prefix = 'gen_'
    return shorten_container_id(prefix + uuid4().hex)


def _recover_saved_containers_from_path(saved_containers_path):
    wait_for_consul_ready()
    try:
        not_recovered = recover_containers_from_kv_store()
        if not_recovered:
            get_logger().error('Following containers were not recovered: %s', not_recovered)
            return False
        else:
            return True
    except:
        get_logger().exception('Unable to recover from %s.', saved_containers_path)
    return False


def _check_if_we_should_recover(saved_containers_path):
    try:
        if int(os.environ.get('DOCKER_START_TIMESTAMP')) > int(os.path.getmtime(saved_containers_path)):
            get_logger().info('Docker daemon restart detected.')
            return True
        else:
            get_logger().info('No need to recover.')
            return False
    except:
        return False


def _get_crashed_services():
    ship = get_ship_name()
    services_list = kv.kv_list('ships/{}/service/'.format(ship))
    crashed_services = []
    if not services_list:
        return crashed_services

    for service in services_list:
        service_dict = kv.kv_get(service)
        microservice_status = service_dict['Status']
        if microservice_status in ['crashed', 'not-recovered']:
            crashed_services.append(service)
    return crashed_services


def _add_running_services_at_startup():
    wait_for_consul_ready()
    try:
        ship = get_ship_name()
        containers_saved_in_kv = kv.kv_list('ships/{}/service/'.format(ship))
        sleep(10)
        all_services = consul_query('agent/services')
        del all_services['consul']
        for service_id, service_dict in all_services.items():
            if ':' in service_id:
                continue
            if service_dict['Service'] == 'armada':
                continue
            key = 'ships/{}/service/{}/{}'.format(ship, service_dict['Service'], service_id)
            if not containers_saved_in_kv or key not in containers_saved_in_kv:
                kv.save_container(ship, service_id, 'started')
                get_logger().info('Added running service: {}'.format(service_id))
    except:
        get_logger().exception('Unable to add running services.')


def recover_containers_from_kv_store():
    services_to_be_recovered = _get_crashed_services()

    for service in services_to_be_recovered:
        kv.update_container_status('recovering', key=service)

    recovery_retry_count = 0
    while services_to_be_recovered and recovery_retry_count < RECOVERY_RETRY_LIMIT:
        get_logger().info("Recovering containers: %s", json.dumps(services_to_be_recovered))
        services_not_recovered = []

        for service in services_to_be_recovered:
            service_parameters = kv.kv_get(service)['params']
            if not _recover_container(service_parameters):
                services_not_recovered.append(service)
            else:
                kv.kv_remove(service)
        sleep(DELAY_BETWEEN_RECOVER_RETRY_SECONDS)
        services_to_be_recovered = services_not_recovered
        recovery_retry_count += 1

    for service in services_to_be_recovered:
        kv.update_container_status('not-recovered', key=service)

    return services_to_be_recovered


def recover_saved_containers_from_parameters(saved_containers):
    wait_for_consul_ready()
    try:
        ship = get_ship_name()
        if isinstance(saved_containers, dict):
            _load_from_dict(saved_containers, ship)
        else:
            _load_from_list(saved_containers, ship)
    except Exception as e:
        get_logger().exception(e)

    containers_to_be_recovered = recover_containers_from_kv_store()
    return containers_to_be_recovered


def main():
    setup_sentry()
    try:
        args = _parse_args()
        _add_running_services_at_startup()
        if args.force or _check_if_we_should_recover(args.saved_containers_path):
            _load_containers_to_kv_store(args.saved_containers_path)
            if not recover_containers_from_kv_store():
                sys.exit(1)
    finally:
        with open(RECOVERY_COMPLETED_PATH, 'w') as recovery_completed_file:
            recovery_completed_file.write('1')


if __name__ == '__main__':
    main()
