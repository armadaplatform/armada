from subprocess import check_output


def get_armada_host_ip():
    output = check_output(['ip', 'route']).decode()
    for line in output.splitlines():
        if line.startswith('default'):
            return line.split()[2]
    return '172.17.0.1'


ARMADA_API_URL = 'http://{}:8900'.format(get_armada_host_ip())
