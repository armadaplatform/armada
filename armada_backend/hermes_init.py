import json
import logging
import socket
import time

import requests

from armada_backend.utils import get_container_ssh_address, initialize_logger
from armada_command.consul.consul import consul_query

HERMES_DIRECTORY = '/etc/opt'


def _consul_discover(service_name):
    service_addresses = set()
    query = 'health/service/{service_name}'.format(service_name=service_name)
    instances = consul_query(query)

    for instance in instances:
        service_checks_statuses = (check['Status'] for check in instance['Checks'])
        if any(status == 'critical' for status in service_checks_statuses):
            continue

        service_ip = instance['Node']['Address']
        service_port = instance['Service']['Port']
        service_address = '{service_ip}:{service_port}'.format(
            service_ip=service_ip, service_port=service_port)

        service_addresses.add(service_address)
    return service_addresses


def _wait_for_armada_start():
    armada_is_running = False

    timeout_expiration = time.time() + 30
    while time.time() < timeout_expiration:
        time.sleep(1)
        try:
            health_status = requests.get('http://localhost/health').text
            if health_status == 'ok':
                armada_is_running = True
                break
        except:
            pass
    if not armada_is_running:
        logging.error('Could not connect to armada.')
        return


def _get_courier_addresses():
    courier_addresses = set()
    courier_is_running = False

    timeout_expiration = time.time() + 30
    while time.time() < timeout_expiration:
        time.sleep(1)
        try:
            courier_addresses = _consul_discover('courier')
            if courier_addresses:
                courier_is_running = True
                break
        except:
            pass
    if not courier_is_running:
        logging.info('No running couriers found.')
    return courier_addresses


def _fetch_hermes_from_couriers(courier_addresses):
    my_ssh_address = get_container_ssh_address(socket.gethostname())
    for courier_address in courier_addresses:
        courier_url = 'http://{courier_address}/update_hermes'.format(**locals())
        try:
            payload = {'ssh': my_ssh_address, 'path': HERMES_DIRECTORY}
            requests.post(courier_url, json.dumps(payload))
        except Exception as e:
            logging.error('Fetching all sources from courier {courier_address} failed: {e}'.format(**locals()))


def main():
    initialize_logger()
    _wait_for_armada_start()

    # We fetch data from courier as soon as possible to cover most common case of 1 courier running.
    courier_addresses = _get_courier_addresses()
    _fetch_hermes_from_couriers(courier_addresses)

    # We fetch data from other couriers that could register a little bit later.
    time.sleep(11)
    new_courier_addresses = _get_courier_addresses() - courier_addresses
    _fetch_hermes_from_couriers(new_courier_addresses)


if __name__ == '__main__':
    main()
