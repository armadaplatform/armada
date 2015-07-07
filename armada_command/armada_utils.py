from __future__ import print_function
import os
import sys
import subprocess
from armada_command.consul.consul import consul_query


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
        try:
            query = 'catalog/service/{service_name}'.format(**locals())
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
