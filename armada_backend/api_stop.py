import traceback
import api_base
import docker_client
from utils import deregister_services

class Stop(api_base.ApiCommand):
    def POST(self):
        container_id, error = self.get_post_parameter('container_id')
        if error:
            return self.status_error(error)
        try:
            self._stop_service(container_id)
            return self.status_ok()
        except Exception as e:
            return self.status_exception("Cannot stop requested container", e)

    def _stop_service(self, container_id):
        docker_api = docker_client.api()
        docker_api.stop(container_id)
        try:
            deregister_services(container_id)
        except Exception as e:
            traceback.print_exc()
