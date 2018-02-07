import logging

import falcon

from armada_backend import api_base, docker_client
from armada_backend.exceptions import BadRequestException
from armada_backend.models.services import update_service_dict, save_container, is_subservice
from armada_backend.models.ships import get_ship_name
from armada_backend.utils import exists_service
from armada_command.consul.consul import consul_post
from armada_command.consul.kv import kv_set, kv_remove


def register_service_in_consul(microservice_data):
    if exists_service(microservice_data['microservice_id']):
        return
    consul_service_data = {
        'ID': microservice_data['microservice_id'],
        'Name': microservice_data['microservice_name'],
        'Port': microservice_data['microservice_port'],
        'Check': {
            'TTL': '15s',
        }
    }
    microservice_tags = microservice_data.get('microservice_tags')
    if microservice_tags:
        consul_service_data['Tags'] = microservice_tags
    response = consul_post('agent/service/register', consul_service_data)
    response.raise_for_status()

    container_id = microservice_data['microservice_id'].split(':')[0]

    kv_set('start_timestamp/{}'.format(container_id), str(microservice_data['container_created_timestamp']))

    key = 'single_active_instance/{}'.format(microservice_data['microservice_id'])
    if microservice_data.get('single_active_instance'):
        kv_set(key, True)
    else:
        kv_remove(key)


def local_port_to_external_port(container_id, microservice_local_port):
    docker_api = docker_client.api()
    docker_inspect = docker_api.inspect_container(container_id)
    container_ports = docker_inspect['NetworkSettings']['Ports']
    if microservice_local_port not in container_ports:
        raise BadRequestException(
            'Container with id="{}" does not expose port "{}"'.format(container_id, microservice_local_port))
    external_port = int(container_ports[microservice_local_port][0]['HostPort'])
    return external_port


class Register(api_base.ApiCommand):
    def on_post(self, req, resp):
        try:
            microservice_data = req.json
            register_service_in_consul(microservice_data)
            result = {'microservice_data': microservice_data}
        except Exception as e:
            return self.status_exception(resp, 'Could not register service.', e)
        return self.status_ok(resp, {'result': result})


class RegisterV1(api_base.ApiCommand):
    def on_post(self, req, resp, microservice_id):
        try:
            input_json = req.json
            container_id = microservice_id.split(':')[0]
            microservice_name = input_json['microservice_name']
            microservice_data = {
                'microservice_id': microservice_id,
                'microservice_name': microservice_name,
                'single_active_instance': bool(input_json.get('single_active_instance')),
                'container_created_timestamp': input_json['container_created_timestamp'],
                'microservice_port': local_port_to_external_port(container_id, input_json['microservice_local_port']),
            }
            microservice_tags = []
            if input_json.get('microservice_env'):
                microservice_tags.append('env:{}'.format(input_json['microservice_env']))
            if input_json.get('microservice_app_id'):
                microservice_tags.append('app_id:{}'.format(input_json['microservice_app_id']))
            if microservice_tags:
                microservice_data['microservice_tags'] = microservice_tags
            microservice_version = input_json.get('microservice_version')
            register_service_in_consul(microservice_data)
            if microservice_version and microservice_name != 'armada' and not is_subservice(microservice_name):
                ship_name = get_ship_name()
                save_container(ship_name, container_id, status='started')
                update_service_dict(ship_name, microservice_name, container_id,
                                    'microservice_version', microservice_version)
            resp.json = microservice_data
        except Exception as e:
            logging.exception(e)
            resp.json = {'error': 'Could not register service: {}'.format(repr(e))}
            resp.status = falcon.HTTP_400
