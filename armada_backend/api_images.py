from armada_backend import api_base, docker_client
from armada_command.scripts.compat import json


class Images(api_base.ApiCommand):
    def on_get(self, req, resp, image_name):
        try:
            docker_api = docker_client.api()
            image_info = json.dumps(docker_api.images(image_name))
            return self.status_ok(resp, {'image_info': '{image_info}'.format(**locals())})
        except Exception as e:
            return self.status_exception(resp, "Cannot get info about image.", e)
