import logging
import os
import time
import xmlrpc.client
from socket import gethostname

import six

from armada_backend import api_base, consul_config
from armada_backend.api_list import get_list
from armada_backend.models.services import get_local_services
from armada_backend.models.ships import get_ship_name, set_ship_name, get_other_ship_ips
from armada_backend.runtime_settings import override_runtime_settings
from armada_backend.utils import deregister_services, get_current_datacenter, get_logger
from armada_command.consul import kv
from armada_command.consul.consul import consul_query, consul_put
from armada_command.scripts.compat import json


def _get_current_consul_mode():
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
    last_exception = None
    while time.time() < timeout_expiration:
        time.sleep(1)
        try:
            armada_instances = get_list('armada', local=True)
            if armada_instances[0]['status'] == 'passing':
                return True
        except Exception as e:
            last_exception = e
    if last_exception:
        logging.exception(last_exception)
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
    def on_get(self, req, resp):
        resp.content_type = 'text/plain'
        resp.body = get_ship_name()

    def on_post(self, req, resp):
        ship_name, error = self.get_post_parameter(req, 'name')
        if error:
            return self.status_error(resp, error)
        other_ship_names = [get_ship_name(ip) for ip in get_other_ship_ips()]
        name_taken = ship_name in other_ship_names
        if not ship_name or ship_name == 'None' or name_taken:
            return self.status_error(resp, 'Incorrect ship name: {}'.format(ship_name))
        set_ship_name(ship_name)
        return self.status_ok(resp)


class Join(api_base.ApiCommand):
    def on_post(self, req, resp):
        consul_host, error = self.get_post_parameter(req, 'host')
        if error:
            return self.status_error(resp, error)
        ship = get_ship_name()
        local_services_data = {key: kv.kv_get(key) for key in get_local_services()}

        armada_size = _get_armada_size()
        if armada_size > 1:
            return self.status_error(resp, 'Currently only single ship armadas can join the others. '
                                           'Your armada has size: {0}.'.format(armada_size))

        try:
            agent_self_dict = consul_query('agent/self', consul_address='{0}:8500'.format(consul_host))
            datacenter = agent_self_dict['Config']['Datacenter']
        except:
            return self.status_error(resp, 'Could not read remote host datacenter address.')

        current_consul_mode = _get_current_consul_mode()
        if current_consul_mode == consul_config.ConsulMode.BOOTSTRAP:
            override_runtime_settings(consul_mode=consul_config.ConsulMode.CLIENT,
                                      ship_ips=[consul_host],
                                      datacenter=datacenter)
        else:
            override_runtime_settings(ship_ips=[consul_host] + get_other_ship_ips(),
                                      datacenter=datacenter)

        if _restart_consul():
            supervisor_server = xmlrpc.client.Server('http://localhost:9001/RPC2')
            hermes_init_output = supervisor_server.supervisor.startProcessGroup('hermes_init')
            get_logger().info('hermes_init start: %s', hermes_init_output)
            set_ship_name(ship)
            for key, data in six.iteritems(local_services_data):
                kv.kv_set(key, data)
            return self.status_ok(resp)
        return self.status_error(resp, 'Waiting for armada restart timed out.')


class Promote(api_base.ApiCommand):
    def on_post(self, req, resp):
        current_consul_mode = _get_current_consul_mode()

        if current_consul_mode == consul_config.ConsulMode.SERVER:
            return self.status_ok(resp, {'message': 'Ship is already in server mode.'})

        if current_consul_mode == consul_config.ConsulMode.BOOTSTRAP:
            return self.status_error(resp, 'Ship must join armada to be promoted to server.')

        override_runtime_settings(consul_mode=consul_config.ConsulMode.SERVER)

        if _restart_consul():
            return self.status_ok(resp)
        return self.status_error(resp, 'Waiting for armada restart timed out.')


class Shutdown(api_base.ApiCommand):
    def on_post(self, req, resp):
        try:
            # 'startsecs=0' is to avoid restarting consul after `consul leave`.
            os.system('sed -i \'/autorestart=true/cautorestart=false\' /etc/supervisor/conf.d/consul.conf')
            os.system('echo startsecs=0 >> /etc/supervisor/conf.d/consul.conf')

            os.system('supervisorctl update consul')

            # As 'supervisorctl update' will restart Consul, we have to wait for it to be running.
            deadline = time.time() + 15
            while time.time() < deadline:
                try:
                    get_current_datacenter()
                    break
                except:
                    time.sleep(1)

            deregister_services(gethostname())
            os.system('consul leave')
        finally:
            post_data = json.loads(req.stream.read() or '{}')
            runtime_settings_path = '/opt/armada/runtime_settings.json'
            if not post_data.get('keep-joined') and os.path.isfile(runtime_settings_path):
                with open(runtime_settings_path) as f:
                    runtime_settings = json.load(f)
                runtime_settings['ships'] = []
                runtime_settings['is_commander'] = True
                with open(runtime_settings_path, 'w') as f:
                    json.dump(runtime_settings, f, sort_keys=True, indent=4)
        return self.status_ok(resp, {'message': 'Shutdown complete.'})
