import argparse
import os
import re
import sys
from collections import Counter
from time import sleep
from uuid import uuid4

import six

from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.models.services import save_container, get_local_services, create_consul_services_key, \
    update_container_status
from armada_backend.models.ships import get_ship_name
from armada_backend.utils import get_logger, shorten_container_id, setup_sentry
from armada_command import armada_api
from armada_command.consul import kv
from armada_command.consul.consul import consul_query
from armada_command.scripts.compat import json

RECOVERY_COMPLETED_PATH = '/tmp/recovery_completed'
RECOVERY_RETRY_LIMIT = 5
START_DELAY_BETWEEN_RECOVER_RETRY = 20
MAX_DELAY_BETWEEN_RECOVER_RETRY = 90


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('saved_containers_path')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    return parser.parse_args()


def _load_saved_containers_parameters(running_containers_parameters_path):
    with open(running_containers_parameters_path) as f:
        return json.load(f)


def _convert_to_consul_services_format(services_parameters):
    new_format = {}
    for key, params in six.iteritems(services_parameters):
        pattern = re.compile(
            r'ships/(?P<ship>.*)/service/(?P<service_name>.*)/(?P<container_id>.*)')
        match = pattern.match(key)

        consul_key_params = {
            'ship': match.group("ship"),
            'service_name': match.group("service_name"),
            'container_id': match.group("container_id"),
        }
        new_format[create_consul_services_key(**consul_key_params)] = params

    return new_format


def _get_local_running_containers():
    result = []
    for container in get_local_services():
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


def _load_from_dict(services_parameters, ship):
    key = next(iter(six.iterkeys(services_parameters)))

    # convert from armada 1.x format
    # todo: remove in future version
    if key.startswith('ships'):
        services_parameters = _convert_to_consul_services_format(services_parameters)

    saved_containers_list = [saved_container['params'] for saved_container in six.itervalues(services_parameters)]
    _load_from_list(saved_containers_list, ship)


def _load_from_list(saved_containers, ship):
    wait_for_consul_ready()
    running_containers = _get_local_running_containers()
    containers_to_be_added = _multiset_difference(saved_containers, running_containers)
    for container_parameters in containers_to_be_added:
        get_logger().info('Added service: {}'.format(container_parameters))
        save_container(ship, _generate_id(), 'crashed', params=container_parameters)


def _load_containers_to_kv_store(saved_containers_path):
    wait_for_consul_ready()
    try:
        ship = get_ship_name()
        saved_containers = _load_saved_containers_parameters(saved_containers_path)
        _load_from_dict(saved_containers, ship)
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
    except Exception as e:
        get_logger().exception(e)
        return False


def _get_crashed_services():
    services_list = get_local_services()
    crashed_services = []

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
        containers_saved_in_kv = get_local_services()
        sleep(10)
        all_services = consul_query('agent/services')
        if 'consul' in all_services:
            del all_services['consul']
        for service_id, service_dict in six.iteritems(all_services):
            if ':' in service_id:
                continue
            if service_dict['Service'] == 'armada':
                continue
            key = create_consul_services_key(ship, service_dict['Service'], service_id)
            if not containers_saved_in_kv or key not in containers_saved_in_kv:
                save_container(ship, service_id, 'started')
                get_logger().info('Added running service: {}'.format(service_id))
    except Exception:
        get_logger().exception('Unable to add running services.')


def recover_containers_from_kv_store():
    services_to_be_recovered = _get_crashed_services()

    for service in services_to_be_recovered:
        update_container_status('recovering', key=service)

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
        if services_not_recovered:
            sleep(min(START_DELAY_BETWEEN_RECOVER_RETRY * 2 ** recovery_retry_count, MAX_DELAY_BETWEEN_RECOVER_RETRY))
        services_to_be_recovered = services_not_recovered
        recovery_retry_count += 1

    for service in services_to_be_recovered:
        update_container_status('not-recovered', key=service)

    return services_to_be_recovered


def recover_saved_containers_from_parameters(saved_containers):
    wait_for_consul_ready()
    try:
        ship = get_ship_name()
        _load_from_dict(saved_containers, ship)
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
            not_recovered = recover_containers_from_kv_store()
            if not_recovered:
                get_logger().error("Containers not recovered: %s", json.dumps(not_recovered))
                sys.exit(1)
            get_logger().info("All containers recovered :)")
    finally:
        with open(RECOVERY_COMPLETED_PATH, 'w') as recovery_completed_file:
            recovery_completed_file.write('1')


if __name__ == '__main__':
    main()
