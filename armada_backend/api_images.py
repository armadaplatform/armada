from armada_command.scripts.compat import json

from armada_backend import api_base, docker_client


class Images(api_base.ApiCommand):
    def GET(self, image_name):
        try:
            docker_api = docker_client.api()
            image_info = json.dumps(docker_api.images(image_name))
            return self.status_ok({'image_info': '{image_info}'.format(**locals())})
        except Exception as e:
            return self.status_exception("Cannot get info about image.", e)
