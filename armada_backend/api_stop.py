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
            docker_api = docker_client.api()

            docker_api.stop(container_id)
        except Exception as e:
            return self.status_error("Cannot stop requested container. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))

        try:
            deregister_services(container_id)
        except Exception as e:
            traceback.print_exc()

        return self.status_ok()
