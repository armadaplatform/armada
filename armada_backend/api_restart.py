import base64
import json
import traceback

import docker_client
from api_run import Run
from utils import deregister_services


class Restart(Run):
    def POST(self):
        container_id, error = self.get_post_parameter('container_id')
        if error:
            return self.status_error(error)

        docker_api = docker_client.api()

        docker_inspect = docker_api.inspect_container(container_id)

        restart_parameters = {}
        for env_var in docker_inspect['Config']['Env']:
            env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
            if env_key == 'RESTART_CONTAINER_PARAMETERS':
                restart_parameters = json.loads(base64.b64decode(env_value))

        image_path = restart_parameters.get('image_path')
        dockyard_user = restart_parameters.get('dockyard_user')
        dockyard_password = restart_parameters.get('dockyard_password')
        dict_ports = restart_parameters.get('ports')
        dict_environment = restart_parameters.get('environment')
        dict_volumes = restart_parameters.get('volumes')
        run_command = restart_parameters.get('run_command')
        microservice_name = dict_environment.get('MICROSERVICE_NAME')
        dockyard_address, _, _ = self._split_image_path(image_path)
        docker_api = self._get_docker_api(dockyard_address, dockyard_user, dockyard_password)

        try:
            self._pull_latest_image(docker_api, image_path, microservice_name)
        except Exception as e:
            return self.status_error("Failed to pull image's newest version. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))
        try:
            docker_api.stop(container_id)
        except Exception as e:
            return self.status_error("Cannot stop requested container. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))

        try:
            deregister_services(container_id)
        except:
            traceback.print_exc()

        return self.run_container(image_path, dockyard_user, dockyard_password, dict_ports, dict_environment,
                                  dict_volumes, run_command)
