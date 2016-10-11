import argparse

import traceback
from time import sleep


from armada_backend.api_ship import wait_for_consul_ready
from armada_backend.utils import get_logger, get_ship_name
from armada_command.consul import kv
from armada_command.consul.consul import consul_query
from armada_backend.recover_saved_containers import _load_containers_to_kv_store


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('saved_containers_path')
    return parser.parse_args()


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
                kv.save_service(ship, service_id, 'started')
                get_logger().info('Added running service: {}'.format(service_id))
    except:
        traceback.print_exc()
        get_logger().error('Unable to add running services.')


def main():
    args = _parse_args()
    _add_running_services_at_startup()
    _load_containers_to_kv_store(args.saved_containers_path)


if __name__ == '__main__':
    main()
