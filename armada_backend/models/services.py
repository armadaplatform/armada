import base64
import calendar
import time

from armada_backend.api_env import get_env
from armada_backend.models.ships import get_ship_name
from armada_command.consul.kv import kv_get, kv_set, kv_list
from armada_command.scripts.compat import json


def save_container(ship, container_id, status, params=None):
    try:
        start_timestamp = kv_get('start_timestamp/{}'.format(container_id))
    except:
        start_timestamp = None
    if status == 'crashed':
        service_name = params['microservice_name']
    else:
        service_name = get_env(container_id, 'MICROSERVICE_NAME')
        if service_name == 'armada':
            return
        params = json.loads(base64.b64decode(get_env(container_id, 'RESTART_CONTAINER_PARAMETERS')))
        if not start_timestamp:
            start_timestamp = str(calendar.timegm(time.gmtime()))
    address = kv_get('ships/{}/ip'.format(ship)) or ship
    service_dict = {
        'ServiceName': service_name,
        'Status': status,
        'container_id': container_id,
        'params': params,
        'start_timestamp': start_timestamp,
        'ServiceID': container_id,
        'Address': address
    }
    kv_set(create_consul_services_key(ship, service_name, container_id), service_dict)


def get_local_services():
    ship = get_ship_name()
    return get_services_by_ship(ship)


def get_services_by_ship(ship=None):
    consul_key = 'services'
    if ship:
        consul_key = '{}/{}'.format(consul_key, ship)

    return kv_list(consul_key) or []


def create_consul_services_key(ship, service_name, container_id):
    return 'services/{ship}/{service_name}/{container_id}'.format(**locals())


def update_container_status(status, ship=None, service_name=None, container_id=None, key=None):
    if not key:
        key = create_consul_services_key(ship, service_name, container_id)
    service_dict = kv_get(key)
    if status == 'crashed' and service_dict['Status'] in ['not-recovered', 'recovering']:
        return
    service_dict['Status'] = status
    kv_set(key, service_dict)


def update_service_dict(ship, service_name, container_id, key, value):
    consul_key = create_consul_services_key(ship, service_name, container_id)
    service_dict = kv_get(consul_key)
    service_dict[key] = value
    kv_set(consul_key, service_dict)


def is_subservice(microservice_name):
    return ':' in microservice_name
