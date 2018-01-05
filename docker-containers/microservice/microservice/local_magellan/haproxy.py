import os
import socket

CONFIG_PATH = '/var/opt/haproxy-local.cfg'
PID_PATH = '/var/run/haproxy-local.pid'
CONFIG_HEADER = '''
global
    daemon
    maxconn 1024

defaults
    mode tcp
    timeout connect 7s
    timeout server 24d
    timeout client 24d

'''


def _is_ip(hostname):
    try:
        socket.inet_aton(hostname)
        return True
    except socket.error:
        return False


def generate_config_from_mapping(port_to_addresses):
    result = CONFIG_HEADER
    for port, addresses in port_to_addresses.items():
        result += '\tlisten service_{port}\n'.format(**locals())
        result += '\t\tbind :::{port} v4v6\n'.format(**locals())
        if not addresses:
            result += '\t\ttcp-request connection reject\n'
        else:
            result += _make_server_config(addresses)
        result += '\n'
    return result


def _make_server_config(addresses):
    result = ""
    for i, address in enumerate(addresses):
        protocol, host = address.split("://", 2) if "://" in address else ("", address)

        result += '\t\tserver server_{i} {host} maxconn 128\n'.format(**locals())
        hostname = host.split(':')[0]
        if protocol == 'http':
            result += '\t\thttp-request del-header Proxy\n'
            if not _is_ip(hostname):
                result += '\t\thttp-request set-header Host {}\n'.format(host)
                result += '\t\tmode {}\n'.format(protocol)
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
    new_config = generate_config_from_mapping(port_to_addresses)
    put_config(new_config)
    restart()
