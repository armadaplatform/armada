from armada_backend import api_base
from armada_backend.recover_saved_containers import recover_containers_from_kv_store
from armada_backend.recover_saved_containers import recover_saved_containers_from_parameters


class Recover(api_base.ApiCommand):
    def POST(self):
        recover_from_kv, error = self.get_post_parameter('recover_from_kv')
        if error:
            return self.status_error(error)
        if recover_from_kv:
            try:
                not_recovered_containers = recover_containers_from_kv_store()
                if not_recovered_containers:
                    return self.status_error(
                        "Failed to recover following containers: {}".format(not_recovered_containers))
            except Exception as e:
                return self.status_exception("Error during containers recovery.", e)
            return self.status_ok()

        saved_containers, error = self.get_post_parameter('saved_containers')
        if error:
            return self.status_error(error)
        try:
            not_recovered_containers = recover_saved_containers_from_parameters(saved_containers)
            if not_recovered_containers:
                return self.status_error(
                    "Failed to recover following containers: {}".format(not_recovered_containers))
        except Exception as e:
            return self.status_exception("Error during containers recovery.", e)
        return self.status_ok()
