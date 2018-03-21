from armada_backend import api_base, docker_client
from armada_command.docker_utils.images import LocalArmadaImage
from armada_command.scripts.compat import json


class Images(api_base.ApiCommand):
    def on_get(self, req, resp, image_name_or_address, image_name=None):
        if image_name is None:
            dockyard_address = None
            image_name = image_name_or_address
        else:
            dockyard_address = image_name_or_address
        image = LocalArmadaImage(dockyard_address, image_name)
        try:
            docker_api = docker_client.api()
            image_info = json.dumps(docker_api.images(image.image_path))
            return self.status_ok(resp, {'image_info': '{image_info}'.format(**locals())})
        except Exception as e:
            return self.status_exception(resp, "Cannot get info about image.", e)
