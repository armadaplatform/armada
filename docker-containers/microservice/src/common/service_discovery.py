import requests

from common.docker_client import get_ship_ip


def _get_armada_url():
    return 'http://{}:8900/v1/'.format(get_ship_ip())


def get_services(params=None):
    response = requests.get(_get_armada_url() + 'list', params=params).json()
    return response['result']


def get_service_to_addresses():
    service_to_addresses = {}
    services = get_services()
    for service in services:
        if service['status'] not in ('passing', 'warning'):
            continue
        tags = service['tags']
        service_index = (service['name'], tags.get('env'), tags.get('app_id'))
        if service_index not in service_to_addresses:
            service_to_addresses[service_index] = []
        service_to_addresses[service_index].append(service['address'])
    return service_to_addresses
