import os

from armada_backend import api_base


class GetVersion(api_base.ApiCommand):
    def GET(self):
        return os.environ.get("ARMADA_VERSION", "none")
