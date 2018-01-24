from __future__ import print_function

import argparse
import json
import os
import re
import socket

from common.docker_client import get_docker_inspect

REGISTRATION_DIRECTORY = "/var/opt/service-registration/"
PORT_PATTERN = re.compile(r'^(\d+)(?:/(tcp|udp))?$', re.IGNORECASE)


def _parse_args():
    parser = argparse.ArgumentParser(description='Register service in Armada.')
    _add_arguments(parser)
    return parser.parse_args()


def _add_arguments(parser):
    parser.add_argument('port',
                        default='80',
                        nargs='?',
                        help='Local TCP (default), or UDP port of the registered service. '
                             'Examples: 80, 8080/tcp, 6001/udp. Default 80/tcp.')
    parser.add_argument('-s', '--subservice',
                        help='Name of the subservice. It will be visible in Armada as: '
                             '[microservice_name]:[subservice_name].')
    parser.add_argument('-c', '--health_check', help="Alternative health check path for this service.", default=None)
    parser.add_argument('--single-active-instance', action='store_true',
                        help="Service discovery mechanisms will return max. 1 working instance of such service. "
                             "The rest will have status 'standby'.",
                        default=False)


def _create_service_file(service_filename, service_registration_data):
    service_file_path = REGISTRATION_DIRECTORY + service_filename + ".json"
    with open(service_file_path, "w+") as f:
        json.dump(service_registration_data, f)


def _get_port_and_protocol(args_port):
    m = PORT_PATTERN.match(args_port)
    if m is None:
        raise ValueError('Incorrect format of --port argument. It should match regexp: ^(\d+)(?:/(tcp|udp))?$')
    port, protocol = m.groups()
    port = int(port)
    protocol = (protocol or 'tcp').lower()
    return '{}/{}'.format(port, protocol)


def main():
    args = _parse_args()
    container_id = socket.gethostname()
    docker_inspect = get_docker_inspect(container_id)
    port_and_protocol = _get_port_and_protocol(args.port)
    service_port = int(docker_inspect['NetworkSettings']['Ports'][port_and_protocol][0]['HostPort'])
    service_filename = microservice_name = os.environ.get('MICROSERVICE_NAME')

    service_id = container_id
    full_service_name = microservice_name
    if args.subservice:
        service_id += ':' + args.subservice
        full_service_name += ':' + args.subservice
        service_filename += '-' + args.subservice

    service_data = {
        "service_id": service_id,
        "service_port": service_port,
        "service_name": full_service_name,
        "service_container_port": args.port,
        "single_active_instance": args.single_active_instance,
    }

    if args.health_check:
        service_data["service_health_check_path"] = args.health_check

    _create_service_file(service_filename, service_data)


if __name__ == '__main__':
    main()
