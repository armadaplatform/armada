import six

from armada_backend import api_base, docker_client
from armada_backend.models.services import save_container
from armada_backend.models.ships import get_ship_name
from armada_backend.utils import shorten_container_id
from armada_command.consul.consul import consul_query


class Start(api_base.ApiCommand):
    def _start_container(self, long_container_id):
        docker_api = docker_client.api(timeout=30)
        docker_api.start(long_container_id)

        service_endpoints = {}
        agent_self_dict = consul_query('agent/self')
        service_ip = agent_self_dict['Config']['AdvertiseAddr']

        docker_inspect = docker_api.inspect_container(long_container_id)

        ship = get_ship_name()
        container_id = shorten_container_id(long_container_id)
        save_container(ship, container_id, status='started')

        for container_port, host_address in six.iteritems(docker_inspect['NetworkSettings']['Ports']):
            service_endpoints['{0}:{1}'.format(service_ip, host_address[0]['HostPort'])] = container_port
        return service_endpoints

    def on_post(self, req, resp):
        long_container_id, error = self.get_post_parameter(req, 'long_container_id')
        if error:
            return self.status_error(resp, error)

        try:
            service_endpoints = self._start_container(long_container_id)
            return self.status_ok(resp, {'endpoints': service_endpoints})
        except Exception as e:
            return self.status_exception(resp, "Cannot start service's container", e)
