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
