import base64
import logging
import os

import requests
from raven import Client, setup_logging
from raven.contrib.webpy.utils import get_data_from_request
from raven.handlers.logging import SentryHandler

from armada_backend import docker_client
from armada_command._version import __version__
from armada_command.consul import kv
from armada_command.consul.consul import consul_get
from armada_command.consul.consul import consul_query
from armada_command.scripts.compat import json
from armada_command.ship_config import get_ship_config

sentry_ignore_exceptions = ['KeyboardInterrupt']
sentry_include_path = ['armada_command', 'armada_backend']


def shorten_container_id(long_container_id):
    return long_container_id[:12]


class WebSentryClient(Client):
    def capture(self, event_type, data=None, date=None, time_spent=None, extra=None, stack=None, tags=None, **kwargs):
        request_data = get_data_from_request()
        data.update(request_data)

        return super(WebSentryClient, self).capture(event_type, data, date, time_spent, extra, stack, tags, **kwargs)


def setup_sentry(is_web=False):
    sentry_url = get_ship_config().get('sentry_url', '')

    client_class = WebSentryClient if is_web else Client
    tags = {'ship_IP': get_external_ip()}

    sentry_client = client_class(sentry_url,
                                 include_paths=sentry_include_path,
                                 release=__version__,
                                 auto_log_stacks=True,
                                 ignore_exceptions=sentry_ignore_exceptions,
                                 tags=tags)

    handler = SentryHandler(sentry_client, level=logging.WARNING)
    setup_logging(handler)

    return sentry_client


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
                get_logger().exception(e)
            try:
                kv.kv_remove("single_active_instance/" + service_id)
            except Exception as e:
                get_logger().exception(e)


def get_external_ip():
    """
    It get current external IP address
    """

    return os.environ.get('SHIP_EXTERNAL_IP', '')


def get_ship_ip():
    """
    It get ship advertise IP address.
    It can be different than external IP, when external IP changes after ship first start.
    """

    agent_self_dict = consul_query('agent/self')
    return agent_self_dict['Config']['AdvertiseAddr']


def get_ship_name(ship_ip=None):
    if ship_ip is None:
        ship_ip = get_ship_ip()
    ship_name = kv.kv_get('ships/{}/name'.format(ship_ip)) or ship_ip
    return ship_name


def set_ship_name(new_name):
    ship_ip = get_ship_ip()
    old_name = get_ship_name(ship_ip)
    saved_containers = kv.kv_list('ships/{}/service/'.format(old_name))
    if saved_containers:
        for container in saved_containers:
            new_key = 'ships/{}/service/{}/{}'.format(new_name, container.split('/')[-2], container.split('/')[-1])
            container_dict = kv.kv_get(container)
            kv.kv_set(new_key, container_dict)
            kv.kv_remove(container)
    kv.kv_set('ships/{}/name'.format(ship_ip), new_name)
    kv.kv_set('ships/{}/ip'.format(new_name), ship_ip)
    os.system('sed -i \'s|ships/{}/|ships/{}/|\' /etc/consul.config'.format(old_name, new_name))
    try:
        os.system('/usr/local/bin/consul reload')
    except Exception as e:
        get_logger().exception(e)
    kv.kv_remove('containers_parameters_list/{}'.format(old_name))


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


def get_ship_names():
    try:
        catalog_nodes_dict = consul_query('catalog/nodes')
        ship_names = list(get_ship_name(consul_node['Address']) for consul_node in catalog_nodes_dict)
        return ship_names
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
    return list(set(service['container_id']
                    for service in services_from_api if service['status'] not in ['recovering', 'crashed']))


def is_container_running(container_id):
    docker_api = docker_client.api()
    try:
        inspect = docker_api.inspect_container(container_id)
        return inspect['State']['Running']
    except:
        return False


def run_command_in_container(command, container_id):
    docker_api = docker_client.api()
    try:
        exec_id = docker_api.exec_create(container_id, command)
        docker_api.exec_start(exec_id['Id'])
    except Exception as e:
        get_logger().exception(e)
