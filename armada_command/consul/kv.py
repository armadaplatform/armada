import base64
import json
import calendar
import time
import os
import requests

from armada_command.consul.consul import consul_put, consul_delete, consul_query

DOCKER_SOCKET_PATH = '/var/run/docker.sock'


def kv_get(key):
    query_result = consul_query('kv/{key}'.format(**locals()))
    if query_result is None:
        return None
    return json.loads(base64.b64decode(query_result[0]['Value']))


def kv_set(key, value):
    consul_put('kv/{key}'.format(**locals()), data=value)


def kv_remove(key):
    consul_delete('kv/{key}'.format(**locals()))


def kv_list(key):
    return consul_query('kv/{key}?keys'.format(**locals()))


def save_service(ship, container_id, status, params=None):
    try:
        start_timestamp = kv_get('start_timestamp/{}'.format(container_id))
    except:
        start_timestamp = None
    if status == 'crashed':
        name = params['microservice_name']
    else:
        name = get_env(container_id, 'MICROSERVICE_NAME')
        params = json.loads(base64.b64decode(get_env(container_id, 'RESTART_CONTAINER_PARAMETERS')))
        start_timestamp = str(calendar.timegm(time.gmtime()))
    address = kv_get('ships/{}/ip'.format(ship)) or ship
    service_dict = {
        'ServiceName': name,
        'Status': status,
        'container_id': container_id,
        'params': params,
        'start_timestamp': start_timestamp,
        'ServiceID': container_id,
        'Address': address
    }
    kv_set('ships/{}/service/{}/{}'.format(ship, name, container_id), service_dict)


def update_service_status(status, ship=None, name=None, container_id=None, key=None):
    if not key:
        key = 'ships/{}/service/{}/{}'.format(ship, name, container_id)
    service_dict = kv_get(key)
    service_dict['Status'] = status
    kv_set(key, service_dict)


def __are_we_in_armada_container():
    return os.environ.get('MICROSERVICE_NAME') == 'armada' and os.path.isfile('/.dockerenv')


def __get_armada_address():
    if __are_we_in_armada_container():
        return 'http://127.0.0.1'
    agent_services_dict = consul_query('agent/services')
    for service in agent_services_dict.values():
        if service['Service'] == 'armada':
            return 'http://127.0.0.1:{}'.format(service['Port'])


def get_env(container_id, env):
    url = '{}/env/{}/{}'.format(__get_armada_address(), container_id, env)
    response = requests.get(url)
    response.raise_for_status()
    result = response.json()
    if result['status'] != 'ok':
        raise ArmadaApiException('Armada API did not return correct status: {0}'.format(result))
    return result['value']
