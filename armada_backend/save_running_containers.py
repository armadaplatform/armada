import argparse
import os
import shutil
import sys

from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.recover_saved_containers import RECOVERY_COMPLETED_PATH
from armada_backend.utils import get_ship_name, get_logger, setup_sentry
from armada_command.consul import kv
from armada_command.scripts.compat import json


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('saved_containers_path')
    parser.add_argument('-f', '--force', action='store_true', default=False,
                        help="Don't wait for completed recovery.")
    return parser.parse_args()


def _save_containers_parameters_list_in_file(containers_parameters_list, saved_containers_path):
    temp_file_path = saved_containers_path + '.tmp'
    with open(temp_file_path, 'w') as temp_file:
        json.dump(containers_parameters_list, temp_file, indent=4, sort_keys=True)
    shutil.copyfile(temp_file_path, saved_containers_path)
    os.remove(temp_file_path)


def _save_containers_parameters_list_in_kv_store(containers_parameters_list):
    ship_name = get_ship_name()
    kv.kv_set('containers_parameters_list/{ship_name}'.format(**locals()), containers_parameters_list)


def _is_recovery_completed():
    try:
        with open(RECOVERY_COMPLETED_PATH) as recovery_completed_file:
            if recovery_completed_file.read() == '1':
                return True
    except:
        pass
    return False


def main():
    setup_sentry()
    args = _parse_args()

    saved_containers_path = args.saved_containers_path
    try:
        wait_for_consul_ready()
        ship = get_ship_name()
        saved_containers = kv.kv_list('ships/{}/service/'.format(ship))
        containers_parameters_dict = {}
        if saved_containers:
            for container in saved_containers:
                container_dict = kv.kv_get(container)
                containers_parameters_dict[container] = container_dict

        if containers_parameters_dict:
            try:
                _save_containers_parameters_list_in_kv_store(containers_parameters_dict)
                get_logger().info('Containers have been saved to kv store.')
            except Exception as e:
                get_logger().exception(e)
            if not args.force and not _is_recovery_completed():
                get_logger().warning('Recovery is not completed. Aborting saving running containers.')
                return
            _save_containers_parameters_list_in_file(containers_parameters_dict, saved_containers_path)
            get_logger().info('Containers have been saved to {}.'.format(saved_containers_path))

        else:
            get_logger().info('Aborted saving container because of errors.')
    except Exception as e:
        get_logger().exception(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
