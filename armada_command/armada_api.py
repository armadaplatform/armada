from __future__ import print_function
import json
import requests
import sys
import urllib
from armada_command.consul.consul import consul_query

# We are using docker IP instead of 'localhost' so armada commands can work from inside armada container also.

ARMADA_IP = '172.17.42.1'

def __get_armada_address(ship_name = None):
    if not ship_name:
        agent_services_dict = consul_query('agent/services')
        for service in agent_services_dict.values():
            if service['Service'] == 'armada':
                return 'http://{0}:{1}'.format(ARMADA_IP, str(service['Port']))
    else:
        service_armada_dict = consul_query('catalog/service/armada')
        for service_armada in service_armada_dict:
            if service_armada['Node'] in (ship_name, 'ship-' + ship_name) or service_armada['Address'] == ship_name:
                return 'http://{0}:{1}'.format(service_armada['Address'], service_armada['ServicePort'])

    raise ValueError('Cannot find ship: {ship_name}.'.format(ship_name = ship_name))
    return None

# ===================================================================================================

def get(api_function, arguments = {}, ship_name = None):
    try:
        result = requests.get(__get_armada_address(ship_name) + '/' + api_function + '?' + urllib.urlencode(arguments))
        return result.text
    except Exception as e:
        print("armada API exception: {exception_class} - {exception}".format(
            exception_class = type(e).__name__, exception = str(e)), file = sys.stderr)
    return None


def post(api_function, arguments = {}, ship_name = None):
    try:
        result = requests.post(__get_armada_address(ship_name) + '/' + api_function, json.dumps(arguments))
        return json.loads(result.text)
    except Exception as e:
        print("armada API exception: {exception_class} - {exception}".format(
            exception_class = type(e).__name__, exception = str(e)), file = sys.stderr)
    return None
