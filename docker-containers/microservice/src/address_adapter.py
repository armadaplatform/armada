import socket

import web

from common.service_discovery import get_services


class AddressAdapterException(Exception):
    pass


class SubservicesCache(object):
    subservices = {}

    def get_subservice_address(self, subservice):
        if subservice in self.subservices:
            return self.subservices[subservice]
        container_id = socket.gethostname()
        if subservice:
            service_id = '{container_id}:{subservice}'.format(**locals())
        else:
            service_id = container_id
        local_services = get_services({'local': '1'})
        for service in local_services:
            if service['microservice_id'] == service_id:
                subservice_address = service['address']
                self.subservices[subservice] = subservice_address
                return subservice_address
        raise AddressAdapterException('Could not find subservice: {subservice}.'.format(**locals()))


subservice_cache = SubservicesCache()


class Health(object):
    def GET(self):
        return 'ok'


class AddressAdapter(object):
    def GET(self, subservice=None):
        return subservice_cache.get_subservice_address(subservice)


def main():
    urls = (
        '/health', Health.__name__,
        '/address/(.*)', AddressAdapter.__name__,
        '/address', AddressAdapter.__name__,
        '/', AddressAdapter.__name__,
    )
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
