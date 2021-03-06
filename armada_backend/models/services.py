import base64
import calendar
import time

from requests.exceptions import RequestException

from armada_backend.api_env import get_env
from armada_backend.models.ships import get_ship_ip_and_name
from armada_command.consul.kv import kv_get, kv_set, kv_list
from armada_command.scripts.compat import json


def save_container(ship_name, container_id, status, params=None, start_timestamp=None, ship_ip=None):
    if start_timestamp is None:
        try:
            start_timestamp = kv_get('start_timestamp/{}'.format(container_id))
        except:
            pass
    if status == 'crashed':
        service_name = params['microservice_name']
    else:
        service_name = get_env(container_id, 'MICROSERVICE_NAME')
        if service_name == 'armada':
            return
        params = json.loads(base64.b64decode(get_env(container_id, 'RESTART_CONTAINER_PARAMETERS')).decode())
        if not start_timestamp:
            start_timestamp = str(calendar.timegm(time.gmtime()))

    if ship_ip is not None:
        address = ship_ip
    else:
        try:
            address = kv_get('ships/{}/ip'.format(ship_name)) or ship_name
        except RequestException as e:
            address = None

    service_dict = {
        'ServiceName': service_name,
        'Status': status,
        'container_id': container_id,
        'params': params,
        'start_timestamp': start_timestamp,
        'ServiceID': container_id,
        'Address': address
    }
    kv_set(create_consul_services_key(ship_name, service_name, container_id), service_dict)


def get_local_services_from_kv_store():
    ship_ip, ship_name = get_ship_ip_and_name()
    if ship_name == ship_ip:
        return get_services_by_ship(ship_name)
    return get_services_by_ship(ship_name) + get_services_by_ship(ship_ip)


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
