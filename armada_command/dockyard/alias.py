from armada_command.consul import kv
import requests
import subprocess
from distutils.version import LooseVersion as Version

DOCKYARD_FALLBACK_ALIAS = 'armada'
DOCKYARD_FALLBACK_ADDRESS = 'dockyard.armada.sh'
INSECURE_REGISTRY_ERROR_MSG = (
    "  \n{header} \n"
    "  If you are trying to use dockyard using HTTP protocol make sure that its address "
    "is added to docker insecure registries list, e.g.:\n"
    "\techo DOCKER_OPTS=\\\"\$DOCKER_OPTS --insecure-registry {address}\\\" | sudo tee --append /etc/default/docker\n"
    "\tsudo service docker restart\n"
    "\tsudo service armada restart\n"
    "  All docker containers will be stopped! armada services will be restarted.\n")


def is_dockyard_address_accessible(url):
    try:
        r = requests.get(url + "/_ping", timeout=1)
        return r.status_code == 200 and r.text == "{}"
    except:
        return False


def print_dockyard_unavailability_warning(address, user=None, password=None, header="Warning!"):
    if user and password:
        return

    if is_dockyard_address_accessible("https://" + address):
        return

    if is_dockyard_address_accessible("http://" + address):
        try:
            process = subprocess.Popen("docker version | grep 'Server version:'", shell=True, stdout=subprocess.PIPE)
            docker_version = process.communicate()[0].split('\n')[0].split(": ")[1]

            if Version(docker_version) > Version("1.3.0"):
                process_ps = subprocess.Popen("ps ax | grep 'docker ' | grep '/usr/bin/docker'", shell=True, stdout=subprocess.PIPE)
                docker_process = process_ps.communicate()[0].split('\n')[0]
                docker_commandline = docker_process.split(None, 4)[-1]
                if "--insecure-registry " + address not in docker_commandline:
                    error = INSECURE_REGISTRY_ERROR_MSG.format(header=header, address=address)
                    print(error)
                    return True
        except Exception:
            pass



def set_alias(name, address, user=None, password=None, check_if_accessible=True):
    if check_if_accessible:
        header = " Warning!\n Your dockyard alias has been set BUT:"
        print_dockyard_unavailability_warning(address, user, password, header)
    key = 'dockyard/aliases/{name}'.format(**locals())
    value = {'address': address}
    if user:
        value['user'] = user
    if password:
        value['password'] = password

    will_be_default = len(get_list()) <= 1 and name != DOCKYARD_FALLBACK_ALIAS
    kv.set(key, value)
    if will_be_default:
        set_default(name)


def get_alias(name):
    key = 'dockyard/aliases/{name}'.format(**locals())
    return kv.get(key)


def remove_alias(name):
    key = 'dockyard/aliases/{name}'.format(**locals())
    kv.remove(key)
    if get_default() == name:
        remove_default()


def get_list():
    result_list = []  # Contains dictionaries:
    # {'name': ..., 'is_default':..., 'address':..., ['user':...], ['password':...])
    default_alias = kv.get('dockyard/default')
    aliases_key = 'dockyard/aliases/'
    prefixed_aliases = kv.list(aliases_key) or []
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
    kv.set('dockyard/default', name)


def get_default():
    return kv.get('dockyard/default')


def remove_default():
    kv.remove('dockyard/default')


def get_initialized():
    return kv.get('dockyard/initialized') == '1'


def set_initialized():
    kv.set('dockyard/initialized', '1')
