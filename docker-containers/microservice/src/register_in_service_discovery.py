from __future__ import print_function
import argparse
import json
import os
import socket
import time
import random
import sys
import traceback
import docker
import re
import requests
from datetime import datetime
import calendar
CONSUL_REST_URL = 'http://172.17.42.1:8500/v1/'
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
                        help='Local TCP (default), or UDP port of the registered service. Examples: 80, 8080/tcp, 6001/udp. Default 80/tcp.')
    parser.add_argument('-s', '--subservice',
                        help='Name of the subservice. It will be visible in Armada as: [microservice_name]:[subservice_name].')
    parser.add_argument('-c', '--health_check', help="Alternative health check path for this service.", default=None)


def print_err(*objs):
    print(*objs, file=sys.stderr)


def consul_query(query):
    return json.loads(consul_get(query).text)


def consul_get(query):
    return requests.get(CONSUL_REST_URL + query, timeout=5)


def consul_post(query, data):
    return requests.post(CONSUL_REST_URL + query, data=json.dumps(data), timeout=5)


def consul_put(query, data):
    return requests.put(CONSUL_REST_URL + query, data=json.dumps(data), timeout=5)


def _exists_service(service_id):
    try:
        return service_id in consul_query('agent/services')
    except:
        return False


def _get_docker_inspect(container_id):
    docker_inspect = {}
    docker_api = docker.Client(base_url='unix:///var/run/docker.sock', version='1.15', timeout=5)
    try:
        docker_inspect = docker_api.inspect_container(container_id)
    except Exception as e:
        print("ERROR on getting docker inspect info: {exception_class} - {exception}".format(
            exception_class=type(e).__name__, exception=str(e)), file=sys.stderr)
    return docker_inspect


def _create_tags():
    tag_pairs = [
        ('env', os.environ.get('MICROSERVICE_ENV')),
        ('app_id', os.environ.get('MICROSERVICE_APP_ID')),
    ]
    return ['{k}:{v}'.format(**locals()) for k, v in tag_pairs if v]


def _register_service(service_id, consul_service_data):
    if not _exists_service(service_id):
        print_err('Registering service...')
        response = consul_post('agent/service/register', consul_service_data)
        assert response.status_code == requests.codes.ok
        print_err('Successfully registered.')


def _create_service_file(service_filename, full_service_name, service_id, service_container_port, service_health_check_path=None):
    service_registration_data = {
        "service_id": service_id,
        "service_container_port": service_container_port,
        "service_name": full_service_name
    }
    if service_health_check_path is not None:
        service_registration_data.update({"service_health_check_path": service_health_check_path})

    service_file_path = REGISTRATION_DIRECTORY + service_filename + ".json"
    with open(service_file_path, "w+") as f:
        json.dump(service_registration_data, f)


def _store_start_timestamp(container_id, container_created_string):
    # Converting "2014-12-11T09:24:13.852579969Z" to an epoch timestamp
    docker_timestamp = container_created_string[:-4]
    epoch_timestamp = str(calendar.timegm(datetime.strptime(
        docker_timestamp, "%Y-%m-%dT%H:%M:%S.%f").timetuple()))
    key = "kv/start_timestamp/" + container_id
    if consul_get(key).status_code == requests.codes.not_found:
        response = consul_put(key, epoch_timestamp)
        assert response.status_code == requests.codes.ok

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
    docker_inspect = _get_docker_inspect(container_id)

    port_and_protocol = _get_port_and_protocol(args.port)

    service_port = int(docker_inspect['NetworkSettings']['Ports'][port_and_protocol][0]['HostPort'])
    service_filename = microservice_name = os.environ.get('MICROSERVICE_NAME')

    while True:
        try:
            agent_self_dict = consul_query('agent/self')
            if agent_self_dict['Config']:
                break
        except:
            pass
        time.sleep(1)

    service_id = container_id
    full_service_name = microservice_name
    if args.subservice:
        service_id += ':' + args.subservice
        full_service_name += ':' + args.subservice
        service_filename += "-" + args.subservice

    consul_service_data = {
        'ID': service_id,
        'Name': full_service_name,
        'Port': service_port,
        'Check': {
            'TTL': '15s',
        }
    }
    tags = _create_tags()
    if tags:
        consul_service_data['Tags'] = tags

    print_err('consul_service_data:\n{0}\n'.format(json.dumps(consul_service_data)))

    _create_service_file(service_filename, full_service_name, service_id, args.port, args.health_check)
    while True:
        try:
            _register_service(service_id, consul_service_data)
        except:
            print_err('ERROR on registering service:')
            traceback.print_exc()

        try:
            _store_start_timestamp(container_id, docker_inspect["Created"])
        except:
            print_err('ERROR on storing timestamp:')
            traceback.print_exc()

        time.sleep(10 + random.uniform(-2, 2))


if __name__ == '__main__':
    main()
