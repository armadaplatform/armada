from __future__ import print_function

import json
import os


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        default=os.path.basename(os.getcwd()),
                        help='Name of the microservice to develop. '
                             'Default is the name of current directory.')
    parser.add_argument('-P', '--dynamic_ports', action='store_true',
                        help='Assign dynamic ports, otherwise it will use sticky port in range 4000..4999, based '
                             'on hash from microservice_name.')
    parser.add_argument('-v', '--volume', default=os.getcwd(),
                        help='Volume mounted to /opt/MICROSERVICE_NAME. Default is current directory path.')
    parser.add_argument('--off', action='store_true',
                        help='Turn off development environment.')


def get_armada_develop_env_file_path():
    return '/tmp/armada_develop_env_{}.json'.format(os.getppid())


def save_dev_env_vars(microservice_name, dynamic_ports, microservice_volume):
    path = get_armada_develop_env_file_path()
    with open(path, 'w') as f:
        env_vars = {
            'MICROSERVICE_NAME': microservice_name or '',
            'MICROSERVICE_DYNAMIC_PORTS': '1' if dynamic_ports else '0',
            'MICROSERVICE_VOLUME': microservice_volume or '',
            'ARMADA_DISABLE_VAGRANT_DEV': '1',
        }
        json.dump(env_vars, f)


def command_develop(args):
    off = args.off
    if off:
        path = get_armada_develop_env_file_path()
        if os.path.exists(path):
            os.unlink(path)
        return
    microservice_name = args.microservice_name
    dynamic_ports = args.dynamic_ports
    volume = args.volume
    save_dev_env_vars(microservice_name, dynamic_ports, volume)
