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


def save_dev_env_vars(microservice_name, dynamic_ports, microservice_volume):
    path = '/tmp/armada_develop_env_{}.json'.format(os.getppid())
    with open(path, 'w') as f:
        env_vars = {
            'MICROSERVICE_NAME': microservice_name or '',
            'MICROSERVICE_DYNAMIC_PORTS': '1' if dynamic_ports else '0',
            'MICROSERVICE_VOLUME': microservice_volume or '',
        }
        json.dump(env_vars, f)


def command_develop(args):
    microservice_name = args.microservice_name
    dynamic_ports = args.dynamic_ports
    volume = args.volume
    save_dev_env_vars(microservice_name, dynamic_ports, volume)
