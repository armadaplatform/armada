import base64
import json
import calendar
import docker
from datetime import datetime

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


def save_service(name, index, status, params, container_id=None):
    if container_id is not None:
        start_timestamp = kv_get("start_timestamp/" + container_id)
    else:
        start_timestamp = None
    kv_set('service/{}/{}'.format(name, index), {'ServiceName': name,
                                                 'Status': status,
                                                 'container_id': container_id,
                                                 'params': params,
                                                 'kv_index': index,
                                                 'start_timestamp': start_timestamp,
                                                 'ServiceID': 'kv_{}_{}'.format(name, index)})


def save_service_1(ship, container_id, status):
    docker_api = docker.Client(base_url='unix://' + DOCKER_SOCKET_PATH, version='1.18', timeout=11)
    docker_api.start(container_id)
    docker_inspect = docker_api.inspect_container(container_id)

    service_env = docker_inspect['Config']['Env']
    for variable in service_env:
        if variable.startswith('MICROSERVICE_NAME'):
            name = variable.split('=')[1].encode('utf-8')
        elif variable.startswith('RESTART_CONTAINER_PARAMETERS'):
            params = json.loads(base64.b64decode(variable[len('RESTART_CONTAINER_PARAMETERS')+1:]))
    start_timestamp_string = docker_inspect['Created'][:-4]
    start_timestamp = str(calendar.timegm(datetime.strptime(
        start_timestamp_string, "%Y-%m-%dT%H:%M:%S.%f").timetuple()))

    service_dict = {
        'ServiceName': name,
        'Status': status,
        'container_id': container_id,
        'params': params,
        'start_timestamp': start_timestamp,
        'ServiceID': container_id
    }
    kv_set('ships/{}/service/{}/{}'.format(ship, name, container_id), service_dict)


def update_service_status(status, ship=None, name=None, container_id=None, key=None):
    if not key:
        key = 'ships/{}/service/{}/{}'.format(ship, name, container_id)
    service_dict = kv_get(key)
    service_dict['Status'] = status
    kv_set(key, service_dict)
