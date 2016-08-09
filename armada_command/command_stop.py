from __future__ import print_function

import argparse
import os
import sys
import traceback

import armada_api
import armada_utils
from armada_command.armada_utils import ArmadaCommandException


def parse_args():
    parser = argparse.ArgumentParser(description='Stop running docker containers.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('microservice_handle', nargs='?',
                        help='Name of the microservice or container_id to be stopped. '
                             'If not provided it will use MICROSERVICE_NAME env variable.')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='Stop all matching services. By default only one instance is allowed to be stopped.')


def command_stop(args):
    microservice_handle = args.microservice_handle or os.environ['MICROSERVICE_NAME']
    if not microservice_handle:
        raise ValueError('No microservice name or container id supplied.')

    instances = armada_utils.get_matched_containers(microservice_handle)
    instances_count = len(instances)

    if instances_count > 1:
        if not args.all:
            raise armada_utils.ArmadaCommandException(
                'There are too many ({instances_count}) matching containers. '
                'Provide more specific container_id or microservice name or use -a/--all flag.'.format(**locals()))
        print('Stopping {instances_count} services {microservice_handle}...'.format(**locals()))
    else:
        microservice_name = instances[0]['ServiceName']
        container_id = instances[0]["ServiceID"].split(':')[0]
        print('Stopping service {microservice_name} ({container_id})...'.format(**locals()))

    were_errors = False
    for i, instance in enumerate(instances):
        try:
            if instances_count > 1:
                print('[{0}/{1}]'.format(i + 1, instances_count))
            container_id = instance['ServiceID'].split(':')[0]
            payload = {'container_id': container_id}
            ship_name = instance['Address']
            result = armada_api.post('stop', payload, ship_name=ship_name)

            if result['status'] == 'ok':
                print('Service {container_id} has been stopped.'.format(**locals()))
                if instances_count > 1:
                    print()
            else:
                raise ArmadaCommandException('Stopping error: {0}'.format(result['error']))
        except:
            traceback.print_exc()
            were_errors = True

    if were_errors:
        sys.exit(1)
