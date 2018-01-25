import falcon
import six

from armada_backend import docker_client
from armada_backend.api_base import ApiCommand
from armada_backend.utils import exists_service


def get_container_ports_mapping(container_id):
    docker_api = docker_client.api()
    docker_inspect = docker_api.inspect_container(container_id)
    container_ports = docker_inspect['NetworkSettings']['Ports']
    mapping = {}
    for local_port, host_ports in six.iteritems(container_ports):
        protocol = local_port.split('/')[-1]
        mapping[local_port] = '{}/{}'.format(host_ports[0]['HostPort'], protocol)
    return mapping


class PortsV1(ApiCommand):
    def on_get(self, req, resp, microservice_id):
        if not exists_service(microservice_id):
            resp.status = falcon.HTTP_404
            resp.json = {'error': 'Could not find service "{microservice_id}"'.format(**locals())}
            return
        try:
            container_id = microservice_id.split(':')[0]
            mapping = get_container_ports_mapping(container_id)
            resp.json = mapping
        except Exception as e:
            resp.json = {'error': 'Could not get ports: {}'.format(repr(e))}
            resp.status = falcon.HTTP_500
