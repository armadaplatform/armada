import base64
import os

import requests

from armada_command.consul.consul import consul_put, consul_delete, consul_query
from armada_command.exceptions import ArmadaApiException
from armada_command.scripts.compat import json

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


def kv_get(key):
    query_result = consul_query('kv/{key}'.format(**locals()))
    if query_result is None:
        return None
    return json.loads(base64.b64decode(query_result[0]['Value']))


def kv_get_recurse(key):
    query_result = consul_query('kv/{key}?recurse=true'.format(**locals()))
    if query_result is None:
        return None
    return {item['Key'].replace(key, ''): json.loads(base64.b64decode(item['Value'])) for item in query_result}


def kv_set(key, value):
    consul_put('kv/{key}'.format(**locals()), data=value)


def kv_remove(key):
    consul_delete('kv/{key}'.format(**locals()))


def kv_list(key):
    return consul_query('kv/{key}?keys'.format(**locals()))


def __are_we_in_armada_container():
    return os.environ.get('MICROSERVICE_NAME') == 'armada' and os.path.isfile('/.dockerenv')


def __get_armada_address():
    if __are_we_in_armada_container():
        return 'http://127.0.0.1'
    agent_services_dict = consul_query('agent/services')
    for service in agent_services_dict.values():
        if service['Service'] == 'armada':
            return 'http://127.0.0.1:{}'.format(service['Port'])
