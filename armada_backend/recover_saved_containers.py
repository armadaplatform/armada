import argparse
from collections import Counter
from time import sleep
import json
import os
import traceback
import sys

from armada_backend.api_run import print_err
from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.utils import get_container_parameters, get_local_containers_ids
from armada_command import armada_api


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
    return [get_container_parameters(container_id) for container_id in get_local_containers_ids()]


def _recover_container(container_parameters):
    print('Recovering {container_parameters}...\n'.format(**locals()))
    recovery_result = armada_api.post('run', container_parameters)
    print('Recovered container: {recovery_result}'.format(**locals()))

def _multiset_difference(a, b):
    a_counter = Counter(json.dumps(x, sort_keys=True) for x in a)
    b_counter = Counter(json.dumps(x, sort_keys=True) for x in b)
    difference = a_counter - b_counter
    return [json.loads(x) for x in difference.elements()]


def recover_saved_containers(saved_containers):
    wait_for_consul_ready()
    running_containers = _get_local_running_containers()
    containers_to_be_recovered = _multiset_difference(saved_containers, running_containers)
    recovery_retry_count = 0
    while containers_to_be_recovered and recovery_retry_count < RECOVERY_RETRY_LIMIT:
        print("Recovering containers: ",containers_to_be_recovered)
        for container_parameters in containers_to_be_recovered:
            _recover_container(container_parameters)
        sleep(DELAY_BETWEEN_RECOVER_RETRY_SECONDS)
        running_containers = _get_local_running_containers()
        containers_to_be_recovered = _multiset_difference(saved_containers, running_containers)
        recovery_retry_count += 1
    return containers_to_be_recovered


def _recover_saved_containers_from_path(saved_containers_path):
    try:
        saved_containers = _load_saved_containers_parameters_list(saved_containers_path)
        not_recovered = recover_saved_containers(saved_containers)
        if not_recovered:
            print_err('Following containers were not recovered: ', not_recovered)
            return False
        else:
            return True
    except:
        traceback.print_exc()
        print_err('Unable to recover from {saved_containers_path}.'.format(**locals()))
    return False


def _check_if_we_should_recover(saved_containers_path):
    try:
        if int(os.environ.get('DOCKER_START_TIMESTAMP')) > int(os.path.getmtime(saved_containers_path)):
            print('Docker daemon restart detected.')
            return True
        else:
            print('No need to recover.')
            return False
    except:
        return False


def main():
    try:
        args = _parse_args()
        if args.force or _check_if_we_should_recover(args.saved_containers_path):
            if not _recover_saved_containers_from_path(args.saved_containers_path):
                sys.exit(1)
    finally:
        with open(RECOVERY_COMPLETED_PATH, 'w') as recovery_completed_file:
            recovery_completed_file.write('1')


if __name__ == '__main__':
    main()
