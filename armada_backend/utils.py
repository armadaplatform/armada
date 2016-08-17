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
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    get_logger.logger = logger
    return logger


def deregister_services(container_id):
    services_dict = consul_query('agent/services')
    for service_id, service_dict in services_dict.items():
        if service_id.startswith(container_id):
            consul_get('agent/service/deregister/{service_id}'.format(**locals()))
            try:
                kv.kv_remove("start_timestamp/" + container_id)
            except Exception as e:
                traceback.print_exc()


def get_ship_ip():
    agent_self_dict = consul_query('agent/self')
    return agent_self_dict['Config']['AdvertiseAddr']


def get_ship_name(ship_ip=None):
    if ship_ip is None:
        ship_ip = get_ship_ip()
    ship_name = kv.kv_get('ships/{}/name'.format(ship_ip)) or ship_ip
    return ship_name


def set_ship_name(name):
    ship_ip = get_ship_ip()
    kv.kv_set('ships/{}/name'.format(ship_ip), name)
    kv.kv_set('ships/{}/ip'.format(name), ship_ip)


def get_other_ship_ips():
    try:
        catalog_nodes_dict = consul_query('catalog/nodes')
        ship_ips = list(consul_node['Address'] for consul_node in catalog_nodes_dict)

        my_ship_ip = get_ship_ip()
        if my_ship_ip in ship_ips:
            ship_ips.remove(my_ship_ip)
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
    response.raise_for_status()
    output = response.json()
    if output['status'] == 'ok':
        container_parameters = json.loads(base64.b64decode(output['value']))
        return container_parameters
    return None


def get_local_containers_ids():
    response = requests.get('http://localhost/list?local=1')
    response.raise_for_status()
    list_response = response.json()
    services_from_api = list_response['result']
    return list(set(service['container_id'] for service in services_from_api if service['status'] not in ['recovering',
                                                                                                          'crashed']))


def is_container_running(container_id):
    docker_api = docker_client.api()
    try:
        inspect = docker_api.inspect_container(container_id)
        return inspect['State']['Running']
    except:
        return False
