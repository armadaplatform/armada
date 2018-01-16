import requests

from microservice.common.docker_client import get_ship_ip


class UnsupportedArmadaApiException(Exception):
    pass


def _get_armada_url():
    return 'http://{}:8900/'.format(get_ship_ip())


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


def register_service_in_armada(microservice_id, microservice_name, microservice_port, microservice_tags,
                               container_created_timestamp, single_active_instance):
    post_data = {
        'microservice_id': microservice_id,
        'microservice_name': microservice_name,
        'microservice_port': microservice_port,
        'microservice_tags': microservice_tags,
        'container_created_timestamp': container_created_timestamp,
        'single_active_instance': single_active_instance,
    }
    response = requests.post(_get_armada_url() + 'register', json=post_data)
    response.raise_for_status()


def register_service_in_armada_v1(microservice_id, microservice_name, microservice_local_port, microservice_env,
                                  microservice_app_id, container_created_timestamp, single_active_instance):
    post_data = {
        'microservice_id': microservice_id,
        'microservice_name': microservice_name,
        'microservice_port': microservice_local_port,
        'microservice_env': microservice_env,
        'microservice_app_id': microservice_app_id,
        'container_created_timestamp': container_created_timestamp,
        'single_active_instance': single_active_instance,
    }
    response = requests.post(_get_armada_url() + 'v1/register', json=post_data)
    if response.status_code == 404:
        raise UnsupportedArmadaApiException('Endpoint /v1/register is unavailable.')
    response.raise_for_status()
