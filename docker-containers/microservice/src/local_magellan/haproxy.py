import os

CONFIG_PATH = '/var/opt/haproxy-local.cfg'
PID_PATH = '/var/run/haproxy-local.pid'
CONFIG_HEADER = '''
global
    daemon
    maxconn 1024

defaults
    mode tcp
    timeout connect 5s
    timeout server 24d
    timeout client 24d

'''


def get_current_config():
    if not os.path.exists(CONFIG_PATH):
        return ''
    with open(CONFIG_PATH, 'r') as haproxy_config_file:
        return haproxy_config_file.read()


def generate_config_from_mapping(port_to_addresses):
    result = CONFIG_HEADER
    for port, addresses in port_to_addresses.items():
        result += '\tlisten service_{port}\n'.format(**locals())
        result += '\t\tbind *:{port}\n'.format(**locals())
        if not addresses:
            result += '\t\ttcp-request connection reject\n'
        else:
            for i, address in enumerate(addresses):
                result += '\t\tserver server_{i} {address} maxconn 128\n'.format(**locals())
        result += '\n'
    return result


def put_config(config):
    with open(CONFIG_PATH, 'w') as haproxy_config_file:
        haproxy_config_file.write(config)


def restart():
    try:
        with open(PID_PATH, 'r') as pid_file:
            pid = pid_file.read()
    except IOError:
        pid = None
    command = 'haproxy -f {config_path} -p {pid_path}'.format(config_path=CONFIG_PATH, pid_path=PID_PATH)
    if pid:
        command += ' -sf {pid}'.format(pid=pid)
    os.system(command)


def update_from_mapping(port_to_addresses):
    old_config = get_current_config()
    new_config = generate_config_from_mapping(port_to_addresses)
    if old_config != new_config:
        put_config(new_config)
        restart()
