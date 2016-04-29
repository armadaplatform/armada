import base64
import json
import traceback

import docker_client
from api_run import Run
from utils import deregister_services, split_image_path


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

        image_path = restart_parameters['image_path']
        dockyard_user = restart_parameters.get('dockyard_user')
        dockyard_password = restart_parameters.get('dockyard_password')
        environment = restart_parameters.get('environment') or {}
        dockyard_address, image_name, _ = split_image_path(image_path)
        docker_api = self._get_docker_api(dockyard_address, dockyard_user, dockyard_password)

        microservice_name = (restart_parameters.get('microservice_name') or environment.get('MICROSERVICE_NAME') or
                             image_name)
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

        return self._run_service(**restart_parameters)
