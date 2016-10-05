import traceback

import api_base
import docker_client
from armada_command.consul.consul import consul_query
from armada_command.consul.kv import save_service
from utils import shorten_container_id, get_ship_name


class Start(api_base.ApiCommand):
    def _start_container(self, long_container_id):
        docker_api = docker_client.api()
        docker_api.start(long_container_id)

        service_endpoints = {}
        agent_self_dict = consul_query('agent/self')
        service_ip = agent_self_dict['Config']['AdvertiseAddr']

        docker_inspect = docker_api.inspect_container(long_container_id)

        ship = get_ship_name()
        container_id = shorten_container_id(long_container_id)
        save_service(ship, container_id, status='started')

        for container_port, host_address in docker_inspect['NetworkSettings']['Ports'].items():
            service_endpoints['{0}:{1}'.format(service_ip, host_address[0]['HostPort'])] = container_port
        return service_endpoints

    def POST(self):
        long_container_id, error = self.get_post_parameter('long_container_id')
        if error:
            return self.status_error(error)

        try:
            service_endpoints = self._start_container(long_container_id)
            return self.status_ok({'endpoints': service_endpoints})
        except Exception as e:
            traceback.print_exc()
            return self.status_exception("Cannot start service's container", e)
