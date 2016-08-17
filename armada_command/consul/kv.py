import base64
import json

from armada_command.consul.consul import consul_put, consul_delete, consul_query


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
