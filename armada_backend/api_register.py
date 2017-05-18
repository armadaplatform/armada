import web

from armada_backend import api_base
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


class Register(api_base.ApiCommand):
    def POST(self):
        try:
            microservice_data = json.loads(web.data())
            register_service_in_consul(microservice_data)
            result = {'microservice_data': microservice_data}
        except Exception as e:
            return self.status_exception('Could not register service.', e)
        return self.status_ok({'result': result})
