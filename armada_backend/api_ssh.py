import socket

from armada_backend import api_base
from armada_backend.hermes_init import HERMES_DIRECTORY
from armada_backend.utils import get_container_ssh_address


class SshAddress(api_base.ApiCommand):
    def on_get(self, req, resp):
        container_id, error = self.get_get_parameter(req, 'container_id')
        if error:
            return self.status_error(resp, error)

        try:
            ssh_address = get_container_ssh_address(container_id)
        except Exception as e:
            return self.status_exception(resp, "Cannot inspect requested container.", e)

        return self.status_ok(resp, {'ssh': ssh_address})


class HermesAddress(api_base.ApiCommand):
    def on_get(self, req, resp):
        try:
            ssh_address = get_container_ssh_address(socket.gethostname())
        except Exception as e:
            return self.status_exception(resp, "Cannot inspect own container.", e)

        return self.status_ok(resp, {'ssh': ssh_address, 'path': HERMES_DIRECTORY})
