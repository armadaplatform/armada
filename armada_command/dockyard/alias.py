import re
import subprocess
from distutils.version import LooseVersion as Version

from six.moves.urllib.parse import urlparse

from armada_command.armada_utils import print_err
from armada_command.consul import kv
from armada_command.docker_utils.compatibility import get_docker_version

DOCKYARD_FALLBACK_ALIAS = 'armada'
DOCKYARD_FALLBACK_ADDRESS = 'dockyard.armada.sh'
INSECURE_REGISTRY_ERROR_MSG = """
{header}
  If you are trying to use dockyard using HTTP protocol make sure that its
address is added to docker daemon's --insecure-registries argument. See
https://docs.docker.com/engine/articles/configuring/ for how to do this on
various distributions, e.g.:

    echo DOCKER_OPTS=\\\"\$DOCKER_OPTS --insecure-registry {address}\\\" | sudo tee --append /etc/default/docker
    sudo service docker restart
    sudo service armada restart

  All docker containers will be stopped! armada services will be restarted.
"""

DISABLED_REMOTE_HTTP_REGISTRY = """
{header}
 Since Docker v1.8.0 it is impossible to use HTTP dockyard from any host
except from localhost. It is recommended to use HTTPS. However, if you
still want to use HTTP and are aware of the insecurity issues, you can use
work-around and access it by running proxy service:

    armada run armada-bind -d armada -r dockyard-proxy -e SERVICE_ADDRESS={address} -p 5000:80
    armada dockyard set {alias} localhost:5000

"""


def print_http_dockyard_unavailability_warning(address, alias, header="Warning!"):
    docker_version = Version(get_docker_version())

    if docker_version >= Version('1.8.0'):
        if address.split(':')[0] not in ['127.0.0.1', 'localhost']:
            if urlparse(address).scheme:
                http_address = address
            else:
                http_address = 'http://' + address
            message = DISABLED_REMOTE_HTTP_REGISTRY.format(address=http_address, alias=alias, header=header)
            print_err(message)
            return True
        return False

    if docker_version > Version('1.3.0'):
        cmd = 'ps ax | grep $(which docker)'
        ps_output = subprocess.check_output(cmd, shell=True)
        if re.search(r'--insecure-registry[ =]' + re.escape(address) + r'\b', ps_output) is None:
            message = INSECURE_REGISTRY_ERROR_MSG.format(address=address, header=header)
            print_err(message)
            return True

    return False


def set_alias(name, address, user=None, password=None):
    key = 'dockyard/aliases/{name}'.format(**locals())
    value = {'address': address}
    if user:
        value['user'] = user
    if password:
        value['password'] = password

    will_be_default = len(get_list()) <= 1 and name != DOCKYARD_FALLBACK_ALIAS
    kv.kv_set(key, value)
    if will_be_default:
        set_default(name)


def get_alias(name):
    key = 'dockyard/aliases/{name}'.format(**locals())
    return kv.kv_get(key)


def remove_alias(name):
    key = 'dockyard/aliases/{name}'.format(**locals())
    kv.kv_remove(key)
    if get_default() == name:
        remove_default()


def get_list():
    result_list = []  # Contains dictionaries:
    # {'name': ..., 'is_default':..., 'address':..., ['user':...], ['password':...])
    default_alias = kv.kv_get('dockyard/default')
    aliases_key = 'dockyard/aliases/'
    prefixed_aliases = kv.kv_list(aliases_key) or []
    for prefixed_alias in sorted(prefixed_aliases):
        alias_name = prefixed_alias[len(aliases_key):]
        row = {
            'name': alias_name,
            'is_default': default_alias == alias_name,
        }
        row.update(get_alias(alias_name))
        result_list.append(row)
    return result_list


def set_default(name):
    kv.kv_set('dockyard/default', name)


def get_default():
    return kv.kv_get('dockyard/default')


def remove_default():
    kv.kv_remove('dockyard/default')


def get_initialized():
    return kv.kv_get('dockyard/initialized') == '1'


def set_initialized():
    kv.kv_set('dockyard/initialized', '1')
