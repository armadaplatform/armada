import traceback

import api_base
import docker_client
from utils import deregister_services, is_container_running, get_logger, run_command_in_container
import fnmatch
from utils import get_ship_name
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
        service_dict = None
        service_list = kv_list('ships/{}/service/'.format(ship))
        if service_list:
            key = fnmatch.filter(service_list, '*/{}'.format(container_id))
            service_dict = kv_get(key[0]) if key else None
        if service_dict and service_dict['Status'] in ['crashed', 'not-recovered']:
            kv_remove(key[0])
        else:
            run_command_in_container('supervisorctl stop armada_agent', container_id)

            # TODO: Compatibility with old microservice images. Should be removed in future armada version.
            run_command_in_container('supervisorctl stop register_in_service_discovery', container_id)

            docker_api = docker_client.api()
            last_exception = None
            try:
                deregister_services(container_id)
            except:
                traceback.print_exc()
            for i in range(3):
                try:
                    docker_api.stop(container_id)
                    kv_remove(key[0])
                except Exception as e:
                    last_exception = e
                    traceback.print_exc()
                if not is_container_running(container_id):
                    break
            if is_container_running(container_id):
                get_logger().error('Could not stop container: %s', container_id)
                raise last_exception
