import os

from armada_backend import api_base


class GetVersion(api_base.ApiCommand):
    def on_get(self, req, resp):
        resp.body = os.environ.get("ARMADA_VERSION", "none")
