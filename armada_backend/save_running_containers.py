import argparse
import os
import shutil
import sys

from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.models.services import get_ship_name
from armada_backend.recover_saved_containers import RECOVERY_COMPLETED_PATH
from armada_backend.utils import get_logger, setup_sentry
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


def _is_recovery_completed():
    try:
        if os.path.isfile(RECOVERY_COMPLETED_PATH):
            with open(RECOVERY_COMPLETED_PATH) as recovery_completed_file:
                if recovery_completed_file.read() == '1':
                    return True
    except Exception as e:
        get_logger().exception(e)
    return False


def main():
    setup_sentry()
    args = _parse_args()
    saved_containers_path = args.saved_containers_path

    if not args.force and not _is_recovery_completed():
        get_logger().info('Recovery is not completed. Aborting saving running containers.')
        return

    try:
        wait_for_consul_ready()
        containers_parameters_dict = {}
        services_key = 'services/{}'.format(get_ship_name())
        containers_parameters = kv.kv_get_recurse(services_key)

        for key, container_dict in containers_parameters.items():
            containers_parameters_dict[services_key + key] = container_dict

        if not containers_parameters_dict:
            get_logger().info('Aborted saving container because list is empty.')
            return

        _save_containers_parameters_list_in_file(containers_parameters_dict, saved_containers_path)
        get_logger().info('Containers have been saved to {}.'.format(saved_containers_path))

    except Exception as e:
        get_logger().exception(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
