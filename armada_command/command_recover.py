from __future__ import print_function
import argparse
import json
import sys
from time import sleep

import armada_api


def parse_args():
    parser = argparse.ArgumentParser(description='Recover saved containers from file.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('saved_containers_path',
                        help='Path to JSON file with saved containers. They are created in /opt/armada.')


def command_recover(args):
    with open(args.saved_containers_path) as saved_containers_file:
        saved_containers = json.load(saved_containers_file)
    payload = {'saved_containers': saved_containers}
    result = armada_api.post('recover', payload)
    if result['status'] != 'ok':
        print(result['error'])
        sys.exit(1)
    else:
        print('Containers have been restored.')
