from __future__ import print_function
import json
import os
import random
import time
import sys

import consul

import haproxy

MICROSERVICE_ENV = os.environ.get('MICROSERVICE_ENV') or None
MICROSERVICE_APP_ID = os.environ.get('MICROSERVICE_APP_ID') or None
LOCAL_MAGELLAN_CONFIG_DIR_PATH = '/var/opt/local-magellan/'


def print_err(*objs):
    print(*objs, file=sys.stderr)


def save_magellan_config(magellan_config):
    if not os.path.exists(LOCAL_MAGELLAN_CONFIG_DIR_PATH):
        os.makedirs(LOCAL_MAGELLAN_CONFIG_DIR_PATH)
    port = list(magellan_config)[0]
    config_file_name = '{}.json'.format(port)
    config_file_path = os.path.join(LOCAL_MAGELLAN_CONFIG_DIR_PATH, config_file_name)
    with open(config_file_path, 'w') as f:
        f.write(json.dumps(magellan_config))


def read_magellan_configs():
    result = {}
    for config_file_name in os.listdir(LOCAL_MAGELLAN_CONFIG_DIR_PATH):
        config_file_path = os.path.join(LOCAL_MAGELLAN_CONFIG_DIR_PATH, config_file_name)
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

        port_to_addresses[port] = {}
        for service_env in reversed(service_envs):
            service_tuple = (service_dict['microservice_name'], service_env,
                             service_dict.get('app_id'))
            if service_tuple in service_to_addresses:
                port_to_addresses[port] = service_to_addresses[service_tuple]
                break
    return port_to_addresses


def main():
    while True:
        try:
            port_to_services = read_magellan_configs()
            if port_to_services is not None:
                service_to_addresses = consul.get_service_to_addresses()
                port_to_addresses = match_port_to_addresses(port_to_services, service_to_addresses)
                haproxy.update_from_mapping(port_to_addresses)
        except Exception as e:
            print_err("ERROR on updating haproxy: {exception_class} - {exception}".format(
                exception_class=type(e).__name__,
                exception=str(e)))
        time.sleep(10 + random.uniform(-2, 2))


if __name__ == '__main__':
    main()
