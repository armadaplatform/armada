from armada_backend import api_base
from armada_backend.recover_saved_containers import recover_saved_containers


class Recover(api_base.ApiCommand):
    def POST(self):
        saved_containers, error = self.get_post_parameter('saved_containers')
        if error:
            return self.status_error(error)
        try:
            not_recovered_containers = recover_saved_containers(saved_containers)
            if not_recovered_containers:
                return self.status_error("Failed to recover following containers: {containers}"
                                         .format(containers=[container['environment'] for container in not_recovered_containers]))
        except Exception as e:
            return self.status_error("Error during containers recovery. {exception_class} - {exception}"
                                     .format(exception_class=type(e).__name__, exception=str(e)))
        return self.status_ok()
