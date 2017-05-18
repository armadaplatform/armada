from __future__ import print_function

import os
import sys
import traceback

import requests
from armada_utils import is_verbose, print_err, ship_name_to_ip, is_ip

from armada_command.consul.consul import consul_query, ConsulException
from armada_command.exceptions import ArmadaApiException
from armada_command.scripts.compat import json
from armada_command.scripts.utils import get_logger


def __are_we_in_armada_container():
    return os.environ.get('MICROSERVICE_NAME') == 'armada' and os.path.isfile('/.dockerenv')


def __get_armada_address(ship_name=None):
    if not ship_name:
        if __are_we_in_armada_container():
            return 'http://127.0.0.1'
        try:
            agent_services_dict = consul_query('agent/services')
            for service in agent_services_dict.values():
                if service['Service'] == 'armada':
                    return 'http://127.0.0.1:{}'.format(service['Port'])
        except ConsulException as e:
            get_logger(__file__).warning('Could not get armada port from consul ({}), falling back to 8900.'.format(e))
            return 'http://127.0.0.1:8900'
    else:
        if not is_ip(ship_name):
            ship_ip = ship_name_to_ip(ship_name)
        else:
            ship_ip = ship_name
        service_armada_dict = consul_query('catalog/service/armada')
        for service_armada in service_armada_dict:
            if service_armada['Address'] == ship_ip:
                return 'http://{0}:{1}'.format(ship_ip, service_armada['ServicePort'])

    raise ValueError('Cannot find ship: {0}.'.format(ship_name))


def __exception_to_status(e):
    error_msg = "armada API exception: {exception_class} - {exception}".format(
        exception_class=type(e).__name__, exception=str(e))
    return {"status": "error", "error": error_msg}


def get(api_function, arguments=None, ship_name=None):
    arguments = arguments or {}
    try:
        url = __get_armada_address(ship_name) + '/' + api_function
        result = requests.get(url, params=arguments)
        result.raise_for_status()
        return result.text
    except Exception as e:
        if is_verbose():
            traceback.print_exc()
        return __exception_to_status(e)


def get_json(api_function, arguments=None, ship_name=None):
    arguments = arguments or {}
    url = __get_armada_address(ship_name) + '/' + api_function
    response = requests.get(url, params=arguments)
    response.raise_for_status()
    result = response.json()
    if result['status'] != 'ok':
        raise ArmadaApiException('Armada API did not return correct status: {0}'.format(result))
    return result['result']


def post(api_function, arguments=None, ship_name=None):
    arguments = arguments or {}
    try:
        url = __get_armada_address(ship_name) + '/' + api_function
        result = requests.post(url, json=arguments)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        if is_verbose():
            traceback.print_exc()
        return __exception_to_status(e)


def print_result_from_armada_api(result):
    if result['status'] == 'ok':
        result_value = dict(result)
        del result_value['status']
        if result_value:
            print(json.dumps(result_value))
    else:
        if result['status'] == 'error':
            print_err(result.get('error'))
        else:
            print_err(result)
        sys.exit(1)
