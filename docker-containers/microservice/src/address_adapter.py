import json
import socket

import requests
import web


CONSUL_REST_URL = 'http://172.17.42.1:8500/v1/'


def consul_query(query):
    return json.loads(requests.get(CONSUL_REST_URL + query, timeout=5).text)


class AddressAdapterException(Exception):
    pass


class SubservicesCache(object):
    subservices = {}
    advertise_address = None

    def get_advertise_address(self):
        if self.advertise_address:
            return self.advertise_address
        try:
            agent_self_dict = consul_query('agent/self')
            self.advertise_address = agent_self_dict['Config']['AdvertiseAddr']
        except:
            raise AddressAdapterException('Could not acquire advertise IP address.')
        return self.advertise_address

    def get_subservice_address(self, subservice):
        if subservice in self.subservices:
            return self.subservices[subservice]
        container_id = socket.gethostname()
        if subservice:
            service_id = '{container_id}:{subservice}'.format(**locals())
        else:
            service_id = container_id
        services_dict = consul_query('agent/services')
        if service_id in services_dict:
            advertise_address = self.get_advertise_address()
            subservice_port = services_dict[service_id]['Port']
            subservice_address = '{advertise_address}:{subservice_port}'.format(**locals())
            self.subservices[subservice] = subservice_address
            return subservice_address
        else:
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
