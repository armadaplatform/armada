import traceback

import api_base
import docker_client
from utils import deregister_services, get_logger


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
        last_exception = None
        for i in range(3):
            try:
                docker_api.stop(container_id)
                break
            except Exception as e:
                last_exception = e
                traceback.print_exc()
        if last_exception:
            raise last_exception
        try:
            deregister_services(container_id)
        except:
            traceback.print_exc()
