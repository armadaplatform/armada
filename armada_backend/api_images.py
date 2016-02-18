import json

import api_base
import docker_client


class GetInfo(api_base.ApiCommand):
    def GET(self, image_name):
        try:
            docker_api = docker_client.api()
            image_info = json.dumps(docker_api.images(image_name))
            return self.status_ok({'image_info': '{image_info}'.format(**locals())})
        except Exception as e:
            return self.status_error("Cannot get info about image. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))
