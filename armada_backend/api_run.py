from armada_backend.api_create import Create
from armada_backend.api_start import Start
from armada_backend.utils import shorten_container_id


class Run(Create, Start):
    def on_post(self, req, resp):
        try:
            post_data = req.json
        except Exception as e:
            return self.status_exception(resp, 'API Run: Invalid input JSON.', e)

        try:
            short_container_id, service_endpoints = self._run_service(post_data)
            return self.status_ok(resp, {'container_id': short_container_id, 'endpoints': service_endpoints})
        except Exception as e:
            return self.status_exception(resp, "Cannot run service", e)

    def _run_service(self, run_parameters):
        long_container_id = self._create_service(**run_parameters)
        service_endpoints = self._start_container(long_container_id)
        short_container_id = shorten_container_id(long_container_id)
        return short_container_id, service_endpoints
