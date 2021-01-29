import json
import sys

import requests
from microservice.common import docker_client

_CONSUL_TIMEOUT_IN_SECONDS = 7
_SHIP_IP = None


def print_err(*objs):
    print(*objs, file=sys.stderr)


def get_consul_url():
    hostname = docker_client.get_ship_ip()
    url = 'http://{}:8500/v1/'.format(hostname)
    return url


def consul_query(query):
    return json.loads(consul_get(query).text)


def consul_get(query):
    return requests.get(get_consul_url() + query, timeout=_CONSUL_TIMEOUT_IN_SECONDS)


def consul_post(query, data):
    return requests.post(get_consul_url() + query, data=json.dumps(data), timeout=_CONSUL_TIMEOUT_IN_SECONDS)


def consul_put(query, data=None):
    data = data or {}
    return requests.put(get_consul_url() + query, data=json.dumps(data), timeout=_CONSUL_TIMEOUT_IN_SECONDS)
