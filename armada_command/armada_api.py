from __future__ import print_function

import json
import os
import urllib

import requests

from armada_command.consul.consul import consul_query


def __are_we_in_armada_container():
    return os.environ.get('MICROSERVICE_NAME') == 'armada' and os.path.isfile('/.dockerinit')


def __get_armada_address(ship_name=None):
    if not ship_name:
        if __are_we_in_armada_container():
            return 'http://127.0.0.1'
        agent_services_dict = consul_query('agent/services')
        for service in agent_services_dict.values():
            if service['Service'] == 'armada':
                return 'http://127.0.0.1:{}'.format(service['Port'])
    else:
        service_armada_dict = consul_query('catalog/service/armada')
        for service_armada in service_armada_dict:
            if service_armada['Node'] in (ship_name, 'ship-' + ship_name) or service_armada['Address'] == ship_name:
                return 'http://{0}:{1}'.format(service_armada['Address'], service_armada['ServicePort'])

    raise ValueError('Cannot find ship: {ship_name}.'.format(ship_name=ship_name))


def __exception_to_status(e):
    error_msg = "armada API exception: {exception_class} - {exception}".format(
        exception_class=type(e).__name__, exception=str(e))
    return {"status": "error", "error": error_msg}


def get(api_function, arguments=None, ship_name=None):
    arguments = arguments or {}
    try:
        result = requests.get(__get_armada_address(ship_name) + '/' + api_function + '?' + urllib.urlencode(arguments))
        return result.text
    except Exception as e:
        return __exception_to_status(e)


def post(api_function, arguments=None, ship_name=None):
    arguments = arguments or {}
    try:
        result = requests.post(__get_armada_address(ship_name) + '/' + api_function, json.dumps(arguments))
        return result.json()
    except Exception as e:
        return __exception_to_status(e)
