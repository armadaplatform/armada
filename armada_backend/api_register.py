from armada_backend import api_base, docker_client
from armada_command.consul.consul import consul_post, consul_query
from armada_command.consul.kv import kv_set, kv_remove
from armada_command.scripts.compat import json


def _exists_service(service_id):
    try:
        return service_id in consul_query('agent/services')
    except:
        return False


def register_service_in_consul(microservice_data):
    if _exists_service(microservice_data['microservice_id']):
        return
    consul_service_data = {
        'ID': microservice_data['microservice_id'],
        'Name': microservice_data['microservice_name'],
        'Port': microservice_data['microservice_port'],
        'Check': {
            'TTL': '15s',
        }
    }
    if microservice_data['microservice_tags']:
        consul_service_data['Tags'] = microservice_data['microservice_tags']
    response = consul_post('agent/service/register', consul_service_data)
    response.raise_for_status()

    container_id = microservice_data['microservice_id'].split(':')[0]

    kv_set('start_timestamp/{}'.format(container_id), str(microservice_data['container_created_timestamp']))

    key = 'single_active_instance/{}'.format(microservice_data['microservice_id'])
    if microservice_data.get('single_active_instance'):
        kv_set(key, True)
    else:
        kv_remove(key)


def local_port_to_external_port(microservice_id, microservice_local_port):
    docker_api = docker_client.api()
    docker_inspect = docker_api.inspect_container(microservice_id.split(':')[0])
    external_port = int(docker_inspect['NetworkSettings']['Ports'][microservice_local_port][0]['HostPort'])
    return external_port


class Register(api_base.ApiCommand):
    def on_post(self, req, resp):
        try:
            microservice_data = json.load(req.stream)
            register_service_in_consul(microservice_data)
            result = {'microservice_data': microservice_data}
        except Exception as e:
            return self.status_exception(resp, 'Could not register service.', e)
        return self.status_ok(resp, {'result': result})


class RegisterV1(api_base.ApiCommand):
    def on_post(self, req, resp):
        try:
            input_json = json.load(req.stream)
            microservice_data = {
                'microservice_id': input_json['microservice_id'],
                'microservice_name': input_json['microservice_name'],
                'single_active_instance': bool(input_json.get('single_active_instance')),
                'container_created_timestamp': input_json['container_created_timestamp'],
                'microservice_port': local_port_to_external_port(input_json['microservice_id'],
                                                                 input_json['microservice_local_port']),
            }
            microservice_tags = []
            if input_json.get('microservice_env'):
                microservice_tags.append('env:{}'.format(input_json['microservice_env']))
            if input_json.get('microservice_app_id'):
                microservice_tags.append('app_id:{}'.format(input_json['microservice_app_id']))
            if microservice_tags:
                microservice_data['microservice_tags'] = microservice_tags
            register_service_in_consul(microservice_data)
            result = {'microservice_data': microservice_data}
        except Exception as e:
            return self.status_exception(resp, 'Could not register service.', e)
        return self.status_ok(resp, {'result': result})
