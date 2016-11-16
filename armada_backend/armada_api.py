import os

import web

from armada_backend.api_create import Create
from armada_backend.api_env import GetEnv
from armada_backend.api_images import Images
from armada_backend.api_info import Info
from armada_backend.api_list import List
from armada_backend.api_recover import Recover
from armada_backend.api_restart import Restart
from armada_backend.api_run import Run
from armada_backend.api_ship import Name, Join, Promote, Shutdown
from armada_backend.api_ssh import HermesAddress
from armada_backend.api_ssh import SshAddress
from armada_backend.api_start import Start
from armada_backend.api_stop import Stop
from armada_backend.api_version import GetVersion
from armada_backend.utils import setup_sentry


class Health(object):
    def GET(self):
        return 'ok'


def _get_module_path_to_class(c):
    return '.'.join([c.__module__, c.__name__])


def main():
    reload = os.environ.get('ARMADA_AUTORELOAD') == 'true'
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

        '/ssh-address', _get_module_path_to_class(SshAddress),
        '/hermes_address', _get_module_path_to_class(HermesAddress),
        '/env/(.*)/(.*)', _get_module_path_to_class(GetEnv),
        '/version', _get_module_path_to_class(GetVersion),
        '/images/(.*)', _get_module_path_to_class(Images),
        '/list', _get_module_path_to_class(List),
        '/info', _get_module_path_to_class(Info),
    )
    app = web.application(urls, globals(), autoreload=reload)
    app.run()


if __name__ == '__main__':
    setup_sentry(is_web=True)
    main()
