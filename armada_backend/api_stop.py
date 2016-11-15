import fnmatch

from armada_backend import api_base, docker_client
from armada_backend.utils import deregister_services, is_container_running, get_logger, run_command_in_container
from armada_backend.utils import get_ship_name
from armada_command.consul.kv import kv_remove, kv_list, kv_get


class Stop(api_base.ApiCommand):
    def POST(self):
        container_id, error = self.get_post_parameter('container_id')
        if error:
            return self.status_error(error)
        try:
            self._stop_service(container_id)
            return self.status_ok()
        except Exception as e:
            return self.status_exception("Cannot stop requested container", e)

    def _stop_service(self, container_id):
        ship = get_ship_name()
        service_list = kv_list('ships/{}/service/'.format(ship))
        if service_list:
            key = fnmatch.filter(service_list, '*/{}'.format(container_id))
        if not is_container_running(container_id):
            kv_remove(key[0])
            try:
                deregister_services(container_id)
            except Exception as e:
                get_logger().exception(e)
        else:
            run_command_in_container('supervisorctl stop armada_agent', container_id)

            # TODO: Compatibility with old microservice images. Should be removed in future armada version.
            run_command_in_container('supervisorctl stop register_in_service_discovery', container_id)

            docker_api = docker_client.api()
            last_exception = None
            try:
                deregister_services(container_id)
            except Exception as e:
                get_logger().exception(e)
            for i in range(3):
                try:
                    docker_api.stop(container_id)
                    kv_remove(key[0])
                except Exception as e:
                    get_logger().debug(e, exc_info=True)
                    last_exception = e
                if not is_container_running(container_id):
                    break
            if is_container_running(container_id):
                get_logger().error('Could not stop container: %s', container_id)
                raise last_exception
