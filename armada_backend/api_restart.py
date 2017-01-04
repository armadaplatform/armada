import base64
import json
from docker.errors import NotFound

from armada_backend import docker_client
from armada_backend.api_run import Run
from armada_backend.api_stop import Stop
from armada_backend.utils import shorten_container_id
from armada_command import armada_api
from armada_command.consul.kv import kv_get, kv_list


class Restart(Run, Stop):
    def POST(self):
        container_id, error = self.get_post_parameter('container_id')
        vagrant_dev, _ = self.get_post_parameter('vagrant_dev')
        target_ship, _ = self.get_post_parameter('target_ship')
        force_restart, _ = self.get_post_parameter('force')

        if error:
            return self.status_error(error)

        try:
            new_container_id, service_endpoints = self._restart_service(container_id, vagrant_dev, target_ship, force_restart)
            short_container_id = shorten_container_id(new_container_id)
            return self.status_ok({'container_id': short_container_id, 'endpoints': service_endpoints})
        except Exception as e:
            return self.status_exception("Unable to restart service", e)

    def _restart_service(self, container_id, vagrant_dev, target_ship=None, force_restart=False):
        restart_parameters = self._get_restart_parameters(container_id)

        if not restart_parameters:
            raise Exception('Could not get RESTART_CONTAINER_PARAMETERS. Container ID: {}'.format(container_id))

        if vagrant_dev:
            restart_parameters = self._update_parameters(restart_parameters)

        if target_ship:
            return self._restart_service_remote(container_id, restart_parameters,
                                                target_ship, force_restart)
        else:
            return self._restart_service_local(container_id, restart_parameters)

    def _get_restart_parameters(self, container_id):
        try:
            docker_api = docker_client.api()
            docker_inspect = docker_api.inspect_container(container_id)

            for env_var in docker_inspect['Config']['Env']:
                env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
                if env_key == 'RESTART_CONTAINER_PARAMETERS':
                    return json.loads(base64.b64decode(env_value))
        except NotFound:
            service_list = kv_list('ships/')
            for service in service_list:
                if service.split('/')[-1] == container_id:
                    return kv_get(service).get('params')

    def _update_parameters(self, restart_parameters):
        ports = restart_parameters['ports']
        has_dynamic_ports = ('-P' in restart_parameters['run_command']) or \
                            ('--dynamic_ports' in restart_parameters['run_command'])
        latest_image_code = '--use_latest_image_code' in restart_parameters['run_command']
        is_port_80_overridden = any(port_container == 80 for _, port_container in ports.items())

        if not (has_dynamic_ports or is_port_80_overridden):
            restart_parameters['ports']['4999'] = '80'
        if not latest_image_code:
            microservice_path = '/opt/{microservice_name}'.format(**restart_parameters)
            restart_parameters['volumes'][microservice_path] = microservice_path

        restart_parameters['environment']['ARMADA_VAGRANT_DEV'] = '1'
        if ' --hidden_vagrant_dev' not in restart_parameters['run_command']:
            restart_parameters['run_command'] += ' --hidden_vagrant_dev'
        return restart_parameters

    def _restart_service_local(self, container_id, restart_parameters):
        new_container_id = self._create_service(**restart_parameters)
        self._stop_service(container_id)
        service_endpoints = self._start_container(new_container_id)
        return new_container_id, service_endpoints

    def _restart_service_remote(self, container_id, restart_parameters, target_ship, force_restart):
        mounted_volumes = restart_parameters.get('volumes')
        static_ports = restart_parameters.get('ports')

        if (mounted_volumes or static_ports) and not force_restart:
            error = "Cannot restart service on another host. Mounted volumes or static ports detected. \n" \
                    "\tVolumes: {0}\n" \
                    "\tPorts: {1}\n" \
                    "Use --force to restart anyway.".format(mounted_volumes, static_ports)
            raise Exception(error)

        new_container_id = self.__create_service_remote(restart_parameters, target_ship)
        self._stop_service(container_id)
        service_endpoints = self.__start_service_remote(new_container_id, target_ship)

        return new_container_id, service_endpoints

    def __create_service_remote(self, restart_parameters, target_ship):
        result = armada_api.post('create', restart_parameters, ship_name=target_ship)
        if result['status'] != "ok":
            raise Exception(result['error'])
        return result['long_container_id']

    def __start_service_remote(self, container_id, target_ship):
        start_payload = {'long_container_id': container_id}
        start_result = armada_api.post('start', start_payload, ship_name=target_ship)
        if start_result['status'] != "ok":
            raise Exception(start_result['error'])
        return start_result['endpoints']
