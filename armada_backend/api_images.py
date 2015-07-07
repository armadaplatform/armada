import json

import api_base
import docker_client


class GetInfo(api_base.ApiCommand):
    def GET(self, microservice_name):
        try:
            docker_api = docker_client.api()
            image_info = json.dumps(docker_api.images(microservice_name))
            return self.status_ok({'image_info': '{image_info}'.format(**locals())})
        except Exception as e:
            return self.status_error("Cannot inspect requested container. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))
