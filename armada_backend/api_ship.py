import json
import os
import random
import time
from socket import gethostname

import api_base
import consul_config
from armada_backend.utils import deregister_services
from armada_command.consul.consul import consul_query, consul_put
from runtime_settings import override_runtime_settings
from utils import get_ship_name, get_other_ship_ips, get_current_datacenter


def _get_current_consul_mode():
    consul_config_data = None
    with open(consul_config.CONFIG_PATH) as consul_config_json:
        consul_config_data = json.load(consul_config_json)

    if consul_config_data.get('bootstrap_expect'):
        if _get_armada_size() > 1:
            return consul_config.ConsulMode.SERVER
        else:
            return consul_config.ConsulMode.BOOTSTRAP
    if consul_config_data.get('server'):
        return consul_config.ConsulMode.SERVER
    return consul_config.ConsulMode.CLIENT


def _get_armada_size():
    try:
        catalog_nodes_dict = consul_query('catalog/nodes')
        return len(catalog_nodes_dict)
    except:
        return 0


def wait_for_consul_ready(timeout_seconds=60):
    timeout_expiration = time.time() + timeout_seconds
    while time.time() < timeout_expiration:
        time.sleep(1)
        try:
            agent_self_dict = consul_query('agent/self')
            ship_name = agent_self_dict['Config']['NodeName']

            health_service_armada = consul_query('health/service/armada')
            for health_armada in health_service_armada:
                if health_armada['Node']['Node'] == ship_name:
                    if all(check['Status'] == 'passing' for check in health_armada['Checks']):
                        return True
        except:
            pass
    return False


def _restart_consul():
    # Services will be registered again by their script 'register_in_service_discovery'.
    agent_self_dict = consul_query('agent/self')
    node_name = agent_self_dict['Config']['NodeName']
    request_body = json.dumps({'Node': node_name})
    consul_put('catalog/deregister', data=request_body)

    os.system('consul leave')
    return wait_for_consul_ready()


class Name(api_base.ApiCommand):
    def GET(self):
        return get_ship_name()

    def POST(self):
        ship_name, error = self.get_post_parameter('name')
        if error:
            return self.status_error(error)
        if not ship_name or ship_name == 'None':
            try:
                ship_name = get_ship_name()
            except:
                ship_name = str(random.randrange(1000000))

        current_consul_mode = _get_current_consul_mode()
        if current_consul_mode == consul_config.ConsulMode.BOOTSTRAP:
            override_runtime_settings(ship_name=ship_name,
                                      ship_ips=[],
                                      datacenter='dc-' + str(random.randrange(1000000)))
        else:
            override_runtime_settings(ship_name=ship_name)

        if _restart_consul():
            return self.status_ok()
        return self.status_error('Waiting for armada restart timed out.')


class Join(api_base.ApiCommand):
    def POST(self):
        consul_host, error = self.get_post_parameter('host')
        if error:
            return self.status_error(error)

        armada_size = _get_armada_size()
        if armada_size > 1:
            return self.status_error('Currently only single ship armadas can join the others. '
                                     'Your armada has size: {armada_size}.'.format(armada_size=armada_size))

        try:
            agent_self_dict = consul_query('agent/self', consul_address='{consul_host}:8500'.format(**locals()))
            datacenter = agent_self_dict['Config']['Datacenter']
        except:
            return self.status_error('Could not read remote host datacenter address.')

        current_consul_mode = _get_current_consul_mode()
        if current_consul_mode == consul_config.ConsulMode.BOOTSTRAP:
            override_runtime_settings(consul_mode=consul_config.ConsulMode.CLIENT,
                                      ship_ips=[consul_host],
                                      datacenter=datacenter)
        else:
            override_runtime_settings(ship_ips=[consul_host] + get_other_ship_ips(),
                                      datacenter=datacenter)

        if _restart_consul():
            return self.status_ok()
        return self.status_error('Waiting for armada restart timed out.')


class Promote(api_base.ApiCommand):
    def POST(self):
        current_consul_mode = _get_current_consul_mode()

        if current_consul_mode == consul_config.ConsulMode.SERVER:
            return self.status_ok({'message': 'Ship is already in server mode.'})

        if current_consul_mode == consul_config.ConsulMode.BOOTSTRAP:
            return self.status_error('Ship must join armada to be promoted to server.')

        override_runtime_settings(consul_mode=consul_config.ConsulMode.SERVER)

        if _restart_consul():
            return self.status_ok()
        return self.status_error('Waiting for armada restart timed out.')


class Shutdown(api_base.ApiCommand):
    def POST(self):

        # Wpisujemy 'startsecs=0', zeby ubicie consula przez 'consul leave' nie spowodowalo jego restartu.
        os.system('sed -i \'/autorestart=true/cautorestart=false\' /etc/supervisor/conf.d/consul.conf')
        os.system('echo startsecs=0 >> /etc/supervisor/conf.d/consul.conf')

        os.system('supervisorctl update consul')

        # 'supervisorctl update' zrestartuje consula. Czekamy az wystartuje na nowo.
        while True:
            try:
                get_current_datacenter()
                break
            except:
                pass

        deregister_services(gethostname())
        os.system('consul leave')
        return self.status_ok({'message': 'Shutdown complete.'})
