from __future__ import print_function

import sys

import armada_api

from armada_command.scripts.compat import json


def add_arguments(parser):
    parser.add_argument('saved_containers_path',
                        help='Path to JSON file with saved containers. They are created in /opt/armada. '
                             'If not provided, containers saved in K/V store will be recovered.',
                        nargs='?', default='')


def command_recover(args):
    if not args.saved_containers_path:
        payload = {'recover_from_kv': True}
    else:
        with open(args.saved_containers_path) as saved_containers_file:
            saved_containers = json.load(saved_containers_file)
        payload = {'recover_from_kv': False, 'saved_containers': saved_containers}
    result = armada_api.post('recover', payload)
    if result['status'] != 'ok':
        print(result['error'])
        sys.exit(1)
    else:
        print('Containers have been restored.')
