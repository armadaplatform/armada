import falcon as falcon
import json

from armada_backend.api_create import Create
from armada_backend.api_env import GetEnv
from armada_backend.api_health import HealthV1
from armada_backend.api_images import Images
from armada_backend.api_info import Info
from armada_backend.api_list import List
from armada_backend.api_ports import PortsV1
from armada_backend.api_recover import Recover
from armada_backend.api_register import Register, RegisterV1
from armada_backend.api_restart import Restart
from armada_backend.api_run import Run
from armada_backend.api_ship import Name, Join, Promote, Shutdown
from armada_backend.api_ssh import HermesAddress
from armada_backend.api_ssh import SshAddress
from armada_backend.api_start import Start
from armada_backend.api_stop import Stop
from armada_backend.api_version import GetVersion
from armada_backend.utils import setup_sentry_for_falcon


class JSONMiddleware(object):
    def process_request(self, req, resp):
        if req.content_length and req.content_type == 'application/json':
            try:
                req.json = json.loads(req.bounded_stream.read().decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                req.json = None
        else:
            req.json = None

    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(resp, 'json') and resp.json is not None and resp.text is None:
            resp.content_type = 'application/json'
            resp.text = json.dumps(resp.json)


class Health(object):
    def on_get(self, req, resp):
        resp.content_type = 'text/plain'
        resp.text = 'ok'


def _get_module_path_to_class(c):
    return '.'.join([c.__module__, c.__name__])


def main():
    urls = (
        '/health', Health.__name__,
        '/name', _get_module_path_to_class(Name),
        '/join', _get_module_path_to_class(Join),
        '/promote', _get_module_path_to_class(Promote),
        '/shutdown', _get_module_path_to_class(Shutdown),

        '/create', _get_module_path_to_class(Create),
        '/start', _get_module_path_to_class(Start),
        '/run', _get_module_path_to_class(Run),
        '/stop', _get_module_path_to_class(Stop),
        '/restart', _get_module_path_to_class(Restart),
        '/recover', _get_module_path_to_class(Recover),
        '/register', _get_module_path_to_class(Register),

        '/ssh-address', _get_module_path_to_class(SshAddress),
        '/hermes_address', _get_module_path_to_class(HermesAddress),
        '/env/{container_id}/{key}', _get_module_path_to_class(GetEnv),
        '/version', _get_module_path_to_class(GetVersion),
        '/images/{image_name_or_address}', _get_module_path_to_class(Images),
        '/images/{image_name_or_address}/{image_name}', _get_module_path_to_class(Images),
        '/list', _get_module_path_to_class(List),
        '/info', _get_module_path_to_class(Info),

        '/v1/local/register/{microservice_id}', _get_module_path_to_class(RegisterV1),
        '/v1/local/ports/{microservice_id}', _get_module_path_to_class(PortsV1),
        '/v1/local/health/{microservice_id}', _get_module_path_to_class(HealthV1),
    )
    app = falcon.API(middleware=[JSONMiddleware()])
    setup_sentry_for_falcon(app)

    # Adapt ~web.py routes to falcon routes:
    routes = list(zip(urls[::2], urls[1::2]))
    for endpoint, path in routes:
        endpoint_class = eval(path.split('.')[-1])
        app.add_route(endpoint, endpoint_class())

    return app


app = main()
