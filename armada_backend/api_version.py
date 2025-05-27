import os

from armada_backend import api_base


class GetVersion(api_base.ApiCommand):
    def on_get(self, req, resp):
        resp.content_type = 'text/plain'
        resp.text = os.environ.get("ARMADA_VERSION", "none")
