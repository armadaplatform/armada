import base64
import logging
import os

import falcon
import requests
import six
from raven import Client, setup_logging
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


def setup_sentry():
    sentry_url = get_ship_config().get('sentry_url', '')

    tags = {'ship_IP': get_external_ip()}

    sentry_client = Client(sentry_url,
                           include_paths=sentry_include_path,
                           release=__version__,
                           auto_log_stacks=True,
                           ignore_exceptions=sentry_ignore_exceptions,
                           tags=tags)

    handler = SentryHandler(sentry_client, level=logging.WARNING)
    setup_logging(handler)

    return sentry_client


class FalconErrorHandler:
    def __init__(self, sentry_client) -> None:
        self.sentry_client = sentry_client

    def __call__(self, ex, req, resp, params):
        if isinstance(ex, falcon.HTTPNotFound):
            raise ex
        data = {
            'request': {
                'url': req.url,
                'method': req.method,
                'query_string': req.query_string,
                'env': req.env,
                'data': req.params,
                'headers': req.headers,
            }
        }
        message = isinstance(ex, falcon.HTTPError) and ex.title or str(ex)
        exception_id = self.sentry_client.captureException(message=message, data=data)
        if not isinstance(ex, falcon.HTTPError):
            raise falcon.HTTPInternalServerError(exception_id, str(ex))
        raise ex


def setup_sentry_for_falcon(app):
    sentry_url = get_ship_config().get('sentry_url')
    if sentry_url:
        sentry_client = setup_sentry()
        error_handler = FalconErrorHandler(sentry_client)
        app.add_error_handler(Exception, error_handler)
    return app


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
    for service_id, service_dict in six.iteritems(services_dict):
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


def trigger_hook(hook_name, container_id):
    cmd = '/opt/microservice/src/run_hooks.py {}'.format(hook_name)
    run_command_in_container(cmd, container_id)


def exists_service(service_id):
    try:
        return service_id in consul_query('agent/services')
    except:
        return False
