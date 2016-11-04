import json
import socket
import time

import requests

from armada_backend.utils import get_container_ssh_address, get_logger, setup_sentry
from armada_command import armada_api

HERMES_DIRECTORY = '/etc/opt'


def _consul_discover(service_name):
    params = {'microservice_name': service_name}
    services = armada_api.get_json('list', params)
    service_addresses = set()
    for service in services:
        if service['status'] in ['passing','warning']:
            service_addresses.add(service['address'])
    return service_addresses


def _wait_for_armada_start():
    timeout_expiration = time.time() + 30
    while time.time() < timeout_expiration:
        time.sleep(1)
        try:
            health_status = requests.get('http://localhost/health').text
            if health_status == 'ok':
                return
        except:
            pass
    get_logger().error('Could not connect to armada.')


def _get_courier_addresses():
    courier_addresses = set()
    courier_is_running = False

    timeout_expiration = time.time() + 30
    last_exception = None
    while time.time() < timeout_expiration:
        time.sleep(1)
        try:
            courier_addresses = _consul_discover('courier')
            last_exception = None
            if courier_addresses:
                courier_is_running = True
                break
        except Exception as e:
            last_exception = e
    if last_exception is not None:
        get_logger().error('Could not determine if courier is running:')
        get_logger().exception(last_exception)
    elif not courier_is_running:
        get_logger().info('No running couriers found.')
    return courier_addresses


def _fetch_hermes_from_couriers(courier_addresses):
    my_ssh_address = get_container_ssh_address(socket.gethostname())
    for courier_address in courier_addresses:
        courier_url = 'http://{courier_address}/update_hermes'.format(**locals())
        try:
            payload = {'ssh': my_ssh_address, 'path': HERMES_DIRECTORY}
            response = requests.post(courier_url, json.dumps(payload))
            response.raise_for_status()
            if response.text.strip() != 'ok':
                raise Exception('Error response from courier:\n{}'.format(response.text))
        except Exception as e:
            get_logger().error('Fetching all sources from courier %s failed:', courier_address)
            get_logger().exception(e)


def main():
    setup_sentry()
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
