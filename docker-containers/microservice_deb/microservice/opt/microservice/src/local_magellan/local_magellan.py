from __future__ import print_function

import json
import os
import random
import sys
import time
import glob

import haproxy

sys.path.append('/opt/microservice/src')
import common.service_discovery

MICROSERVICE_ENV = os.environ.get('MICROSERVICE_ENV') or None
MICROSERVICE_APP_ID = os.environ.get('MICROSERVICE_APP_ID') or None
LOCAL_MAGELLAN_CONFIG_DIR_PATH = '/var/opt/local-magellan/'
SERVICE_DISCOVERY_CONFIG_PATH = '/var/opt/service_discovery.json'
SERVICE_TO_ADDRESSES_CONFIG_DIR_PATH = '/var/opt/service_to_addresses.json'

def print_err(*objs):
    print(*objs, file=sys.stderr)


def save_magellan_config(magellan_config):
    try:
        os.makedirs(LOCAL_MAGELLAN_CONFIG_DIR_PATH)
    except OSError:
        if not os.path.isdir(LOCAL_MAGELLAN_CONFIG_DIR_PATH):
            raise
    port = list(magellan_config)[0]
    config_file_name = '{0}.json'.format(port)
    config_file_path = os.path.join(LOCAL_MAGELLAN_CONFIG_DIR_PATH, config_file_name)
    with open(config_file_path, 'w') as f:
        f.write(json.dumps(magellan_config))


def read_magellan_configs():
    result = {}
    for config_file_path in glob.glob(os.path.join(LOCAL_MAGELLAN_CONFIG_DIR_PATH, '*.json')):
        with open(config_file_path) as f:
            result.update(json.load(f))
    return result


def match_port_to_addresses(port_to_services, service_to_addresses):
    port_to_addresses = {}
    for port, service_dict in port_to_services.items():
        service_envs = []
        potential_service_env = ''
        env = service_dict.get('env')
        if env:
            for part in env.split('/'):
                potential_service_env += part
                service_envs.append(potential_service_env)
                potential_service_env += '/'
        else:
            service_envs = [env]

        port_to_addresses[port] = []
        for service_env in reversed(service_envs):
            service_tuple = (service_dict['microservice_name'], service_env,
                             service_dict.get('app_id'))
            if service_tuple in service_to_addresses:
                port_to_addresses[port] = service_to_addresses[service_tuple]
                break
    return port_to_addresses


def has_data_changed(port_to_addresses):
    if os.path.exists(SERVICE_TO_ADDRESSES_CONFIG_DIR_PATH):
        with open(SERVICE_TO_ADDRESSES_CONFIG_DIR_PATH, 'r') as f:
            old_config = json.load(f)
            if old_config == port_to_addresses:
                return False
        return True
    return True


def main():
    time.sleep(1)
    first_try = True
    while True:
        try:
            port_to_services = read_magellan_configs()
            if not port_to_services and not first_try:
                sys.exit(0)

            with open(SERVICE_DISCOVERY_CONFIG_PATH, 'w') as f:
                json.dump(port_to_services, f)

            service_to_addresses = common.service_discovery.get_service_to_addresses()
            port_to_addresses = match_port_to_addresses(port_to_services, service_to_addresses)

            if has_data_changed(port_to_addresses):
                with open(SERVICE_TO_ADDRESSES_CONFIG_DIR_PATH, 'w') as f:
                    json.dump(port_to_addresses, f, indent=4, sort_keys=True)
                haproxy.update_from_mapping(port_to_addresses)

        except Exception as e:
            print_err("ERROR on updating haproxy: {exception_class} - {exception}".format(
                exception_class=type(e).__name__,
                exception=str(e)))
        first_try = False
        time.sleep(10 + random.uniform(-2, 2))


if __name__ == '__main__':
    main()
