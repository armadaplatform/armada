import base64
import calendar

import time

from armada_backend.utils import get_ship_name
from armada_command.consul.kv import kv_get, get_env, kv_set, kv_list
from armada_command.scripts.compat import json


def save_container(ship, container_id, status, params=None):
    try:
        start_timestamp = kv_get('start_timestamp/{}'.format(container_id))
    except:
        start_timestamp = None
    if status == 'crashed':
        name = params['microservice_name']
    else:
        name = get_env(container_id, 'MICROSERVICE_NAME')
        params = json.loads(base64.b64decode(get_env(container_id, 'RESTART_CONTAINER_PARAMETERS')))
        if not start_timestamp:
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
    kv_set('services/{ship}/{name}/{container_id}'.format(**locals()), service_dict)


def get_local_services():
    ship = get_ship_name()
    return get_services_by_ship(ship)


def get_services_by_ship(ship):
    return kv_list('services/{ship}/'.format(**locals())) or []
