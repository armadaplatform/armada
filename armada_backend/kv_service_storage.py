import json
import hashlib

from armada_command.consul import kv


def set_status(name, id, status, params):
    kv.kv_set('service/{}/{}'.format(name, id), {'status': status, 'params': params})
