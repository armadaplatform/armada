import web

from api_create import Create
from api_env import GetEnv
from api_images import Images
from api_info import Info
from api_list import List
from api_recover import Recover
from api_restart import Restart
from api_run import Run
from api_ship import Name, Join, Promote, Shutdown
from api_ssh import HermesAddress
from api_ssh import SshAddress
from api_start import Start
from api_stop import Stop
from api_version import GetVersion


class Health(object):
    def GET(self):
        return 'ok'


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

        '/ssh-address', _get_module_path_to_class(SshAddress),
        '/hermes_address', _get_module_path_to_class(HermesAddress),
        '/env/(.*)/(.*)', _get_module_path_to_class(GetEnv),
        '/version', _get_module_path_to_class(GetVersion),
        '/images/(.*)', _get_module_path_to_class(Images),
        '/list', _get_module_path_to_class(List),
        '/info', _get_module_path_to_class(Info),
    )
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
