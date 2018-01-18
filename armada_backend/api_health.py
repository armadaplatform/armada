import falcon

from armada_backend.api_base import ApiCommand
from armada_command.consul.consul import consul_put


def _get_consul_health_endpoint(health_check_code):
    if health_check_code == 0:
        return 'pass'
    if health_check_code == 1:
        return 'warn'
    return 'fail'


class HealthV1(ApiCommand):
    def on_put(self, req, resp, microservice_id):
        try:
            input_json = req.json
            health_check_code = input_json['health_check_code']
            health_endpoint = _get_consul_health_endpoint(health_check_code)
            r = consul_put('agent/check/{}/service:{}'.format(health_endpoint, microservice_id))
            if r.status_code == 404:
                resp.status = falcon.HTTP_404
                resp.json = {'error': 'Could not find service "{}", try registering it first. Details: {}'.format(
                    microservice_id, r.content)}
                return
            r.raise_for_status()
        except Exception as e:
            resp.json = {'error': 'Could not mark service health check status: {}'.format(repr(e))}
            resp.status = falcon.HTTP_400
