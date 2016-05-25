import base64
import json
import logging
import traceback

import requests

from armada_backend import docker_client
from armada_command.consul import kv
from armada_command.consul.consul import consul_get
from armada_command.consul.consul import consul_query


def shorten_container_id(long_container_id):
    return long_container_id[:12]


def get_logger():
    try:
        return get_logger.logger
    except AttributeError:
        pass
    logger = logging.getLogger('armada_backend')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    get_logger.logger = logger
    return logger


def deregister_services(container_id):
    services_dict = consul_query('agent/services')
    for service_id, service_dict in services_dict.items():
        if service_id.startswith(container_id):
            consul_get('agent/service/deregister/{service_id}'.format(**locals()))
            try:
                kv.remove("start_timestamp/" + container_id)
            except Exception as e:
                traceback.print_exc()


def get_ship_name():
    agent_self_dict = consul_query('agent/self')
    ship_name = agent_self_dict['Config']['NodeName']
    if ship_name.startswith('ship-'):
        ship_name = ship_name[5:]
    return ship_name


def get_other_ship_ips():
    try:
        catalog_nodes_dict = consul_query('catalog/nodes')
        ship_ips = list(consul_node['Address'] for consul_node in catalog_nodes_dict)

        agent_self_dict = consul_query('agent/self')
        service_ip = agent_self_dict['Config']['AdvertiseAddr']
        if service_ip in ship_ips:
            ship_ips.remove(service_ip)
        return ship_ips
    except:
        return []


def get_current_datacenter():
    agent_self_dict = consul_query('agent/self')
    return agent_self_dict['Config']['Datacenter']


def is_ship_commander():
    ship_info = consul_query('agent/self')
    if ship_info['Config']['Server']:
        return True
    return False


def get_container_ssh_address(container_id):
    docker_api = docker_client.api()

    docker_inspect = docker_api.inspect_container(container_id)
    ssh_port = docker_inspect['NetworkSettings']['Ports']['22/tcp'][0]['HostPort']

    agent_self_dict = consul_query('agent/self')
    service_ip = agent_self_dict['Config']['AdvertiseAddr']

    return '{service_ip}:{ssh_port}'.format(**locals())


def get_container_parameters(container_id):
    url = 'http://localhost/env/{container_id}/RESTART_CONTAINER_PARAMETERS'.format(**locals())
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        output = response.json()
        if output['status'] == 'ok':
            container_parameters = json.loads(base64.b64decode(output['value']))
            return container_parameters


def get_local_containers_ids():
    response = requests.get('http://localhost/list?local=1')
    assert response.status_code == requests.codes.ok
    list_response = response.json()
    services_from_api = list_response['result']
    return list(set(service['container_id'] for service in services_from_api))


def split_image_path(image_path):
    dockyard_address = None
    image_name = image_path
    image_tag = 'latest'

    if '/' in image_name:
        dockyard_address, image_name = image_name.split('/', 1)
    if ':' in image_name:
        image_name, image_tag = image_name.split(':', 1)

    return dockyard_address, image_name, image_tag
