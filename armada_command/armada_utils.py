from __future__ import print_function

import fnmatch
import os
import socket
import subprocess
import sys

from colored import style
from colored.fore import *

from armada_command.consul.consul import consul_query
from consul import kv


class ArmadaCommandException(Exception):
    pass


def print_err(*objs):
    print(*objs, file=sys.stderr)


def is_local_container(container_id):
    return container_id in (service_id.split(':')[0] for service_id in consul_query('agent/services').keys())


def get_matched_containers(microservice_name_or_container_id_prefix):
    service_names = list(consul_query('catalog/services').keys())

    matched_containers_by_name = []
    matched_containers_by_id = []

    for service_name in service_names:
        query = 'catalog/service/{service_name}'.format(**locals())
        try:
            instances = consul_query(query)
        except Exception as e:
            print_err('WARNING: query "{query}" failed ({exception_class}: {exception})'.format(
                query=query, exception_class=type(e).__name__, exception=e))
            instances = []

        for instance in instances:
            container_id = instance['ServiceID'].split(':')[0]
            service_name = instance['ServiceName']

            if microservice_name_or_container_id_prefix == service_name:
                matched_containers_by_name.append(instance)

            if container_id.startswith(microservice_name_or_container_id_prefix) and ":" not in instance['ServiceID']:
                matched_containers_by_id.append(instance)

    services_list = kv.kv_list('services/')
    if services_list:
        for service in services_list:
            service_dict = kv.kv_get(service)
            container_id = service_dict['container_id']
            service_name = service_dict['ServiceName']

            if service_dict['Status'] == 'started':
                try:
                    instances = consul_query('catalog/service/{}'.format(service_name))
                    if container_id in [i['ServiceID'].split(':')[0] for i in instances]:
                        continue
                except Exception as e:
                    pass

            if microservice_name_or_container_id_prefix == service_name:
                matched_containers_by_name.append(service_dict)

            if container_id.startswith(microservice_name_or_container_id_prefix) \
                    and ":" not in service_dict['ServiceID']:
                matched_containers_by_id.append(service_dict)

    matched_containers_by_name_count = len(matched_containers_by_name)
    matched_containers_by_id_count = len(matched_containers_by_id)

    if matched_containers_by_name_count and matched_containers_by_id_count:
        raise ArmadaCommandException(
            'Found matching containers with both microservice name ({matched_containers_by_name_count}) '
            'and container_id ({matched_containers_by_id_count}). '
            'Please provide more specific criteria.'.format(**locals()))
    if matched_containers_by_id_count > 1:
        raise ArmadaCommandException(
            'There are too many ({matched_containers_by_id_count}) matching containers. '
            'Please provide more specific container_id.'.format(**locals()))
    matched_containers = matched_containers_by_name + matched_containers_by_id

    matches_count = len(matched_containers)
    if matches_count == 0:
        raise ArmadaCommandException(
            'There are no running containers with microservice: '
            '{microservice_name_or_container_id_prefix}'.format(**locals()))

    return matched_containers


def execute_local_command(command, stream_output=False, retries=0):
    code, out, err = None, None, None
    for i in range(retries + 1):
        if i > 0:
            print_err('Retrying... ({i} of {retries})'.format(**locals()))
        if stream_output:
            code = os.system(command)
            out, err = None, None
        else:
            p = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            out, err = p.communicate()
            code = p.returncode
        if code == 0:
            break
        else:
            print_err('Command failed: {command}'.format(**locals()))
    return code, out, err


def is_verbose():
    try:
        return is_verbose.verbose
    except AttributeError:
        return False


def set_verbose():
    is_verbose.verbose = True


def print_table(rows):
    widths = [max(len(str(val)) for val in col) for col in zip(*rows)]
    for row in rows:
        print('  '.join((str(val).ljust(width) for val, width in zip(row, widths))))


def ship_name_to_ip(name):
    return kv.kv_get('ships/{}/ip'.format(name))


def ship_ip_to_name(ip):
    return kv.kv_get('ships/{}/name'.format(ip))


def split_image_path(image_path):
    dockyard_address = None
    image_name = image_path
    image_tag = 'latest'

    if image_path:
        if '/' in image_name:
            dockyard_address, image_name = image_name.split('/', 1)
        if ':' in image_name:
            image_name, image_tag = image_name.split(':', 1)

    return dockyard_address, image_name, image_tag


def is_ip(name):
    try:
        socket.inet_aton(name)
        return True
    except socket.error:
        return False


def is_port_available(port):
    return os.system('nc -z localhost {}'.format(port)) != 0


def notify_about_detected_dev_environment(image_name):
    if os.environ.get('ARMADA_DEVELOP') == '1' and os.environ.get('MICROSERVICE_NAME') == image_name:
        print(style.BOLD + fore.GREEN
              + 'INFO: Detected development environment for microservice "{}".'.format(image_name)
              + style.RESET)

