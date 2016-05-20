import web

from armada_backend.utils import initialize_logger


class Health(object):
    def GET(self):
        return 'ok'


def main():
    initialize_logger()
    urls = (
        '/health', Health.__name__,

        '/name', 'api_ship.Name',
        '/join', 'api_ship.Join',
        '/promote', 'api_ship.Promote',
        '/shutdown', 'api_ship.Shutdown',

        '/create', 'api_create.Create',
        '/start', 'api_start.Start',
        '/run', 'api_run.Run',
        '/stop', 'api_stop.Stop',
        '/restart', 'api_restart.Restart',
        '/recover', 'api_recover.Recover',

        '/ssh-address', 'api_ssh.Address',
        '/hermes_address', 'api_ssh.HermesAddress',
        '/env/(.*)/(.*)', 'api_info.GetEnv',
        '/version', 'api_info.GetVersion',
        '/images/(.*)', 'api_images.GetInfo',
        '/list', 'api_list.List',
    )
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
