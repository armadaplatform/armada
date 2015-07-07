import argparse
import json
import os
import traceback
import shutil
import sys

from api_run import print_err
from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.recover_saved_containers import RECOVERY_COMPLETED_PATH
from armada_backend.utils import get_container_parameters, get_ship_name
from armada_backend.utils import get_local_containers_ids
from armada_command.consul import kv
from armada_command.consul.consul import consul_query


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
    kv.set('containers_parameters_list/{ship_name}'.format(**locals()), containers_parameters_list)


def _is_recovery_completed():
    try:
        with open(RECOVERY_COMPLETED_PATH) as recovery_completed_file:
            if recovery_completed_file.read() == '1':
                return True
    except:
        pass
    return False


def main():
    args = _parse_args()
    if not args.force and not _is_recovery_completed():
        print('Recovery is not completed. Aborting saving running containers.')
        return
    saved_containers_path = args.saved_containers_path
    try:
        wait_for_consul_ready()
        containers_ids = get_local_containers_ids()
        containers_parameters_list = []
        errors_count = 0
        for container_id in containers_ids:
            try:
                container_parameters = get_container_parameters(container_id)
                if container_parameters:
                    containers_parameters_list.append(container_parameters)
            except:
                errors_count += 1
                print_err('ERROR on getting container parameters for {container_id}:'.format(**locals()))
                traceback.print_exc()
        # Don't overwrite saved containers' list if it would become empty because of errors.
        if containers_parameters_list or not errors_count:
            _save_containers_parameters_list_in_file(containers_parameters_list, saved_containers_path)
            print('Containers have been saved to {saved_containers_path}.'.format(**locals()))
            try:
                _save_containers_parameters_list_in_kv_store(containers_parameters_list)
                print('Containers have been saved to kv store.')
            except:
                traceback.print_exc()
        else:
            print('Aborted saving container because of errors.')
    except:
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
