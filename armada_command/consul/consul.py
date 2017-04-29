import requests

from armada_command.scripts.compat import json
from armada_command.scripts.utils import get_logger

CONSUL_ADDRESS = 'localhost:8500'
CONSUL_TIMEOUT_IN_SECONDS = 10

logger = get_logger(__file__)


class ConsulException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return ('ERROR: Local Armada agent is not working properly. '
                'Try restarting armada and/or join with previously connected ships.\n'
                'Failing url: {url}').format(url=self.url)


def __get_consul_url(query, consul_address=None):
    if consul_address is None:
        consul_address = CONSUL_ADDRESS
    return 'http://{consul_address}/v1/{query}'.format(**locals())


def consul_get(query, consul_address=None):
    return requests.get(__get_consul_url(query, consul_address), timeout=CONSUL_TIMEOUT_IN_SECONDS)


def consul_post(query, data, consul_address=None):
    return requests.post(__get_consul_url(query, consul_address), data=json.dumps(data),
                         timeout=CONSUL_TIMEOUT_IN_SECONDS)


def consul_put(query, data, consul_address=None):
    return requests.put(__get_consul_url(query, consul_address), data=json.dumps(data),
                        timeout=CONSUL_TIMEOUT_IN_SECONDS)


def consul_delete(query, consul_address=None):
    return requests.delete(__get_consul_url(query, consul_address), timeout=CONSUL_TIMEOUT_IN_SECONDS)


def consul_query(query, consul_address=None):
    try:
        response = consul_get(query, consul_address)
        if response.status_code == 404:
            return None
        return json.loads(response.text)
    except Exception as e:
        if 'response' in locals() and hasattr(response, 'text'):
            logger.debug(response.text)

        logger.debug(e, exc_info=True)

        raise ConsulException(url=__get_consul_url(query, consul_address))
