import api_base
import socket
from armada_backend.utils import get_container_ssh_address
from armada_backend.hermes_init import HERMES_DIRECTORY

#===================================================================================================

class Address(api_base.ApiCommand):

    def GET(self):
        container_id, error = self.get_get_parameter('container_id')
        if error:
            return self.status_error(error)

        try:
            ssh_address = get_container_ssh_address(container_id)
        except Exception as e:
            return self.status_error("Cannot inspect requested container. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))

        return self.status_ok({ 'ssh': ssh_address })

#===================================================================================================

class HermesAddress(api_base.ApiCommand):

    def GET(self):
        try:
            ssh_address = get_container_ssh_address(socket.gethostname())
        except Exception as e:
            return self.status_error("Cannot inspect own container. {exception_class} - {exception}".format(
                exception_class=type(e).__name__, exception=str(e)))

        return self.status_ok({ 'ssh': ssh_address, 'path': HERMES_DIRECTORY })

#===================================================================================================
