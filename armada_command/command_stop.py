from __future__ import print_function

import os
import six
import sys
import traceback

import armada_api
import armada_utils
from armada_command.armada_utils import ArmadaCommandException


def add_arguments(parser):
    parser.add_argument('microservice_handle', nargs='*',
                        help='Name of the microservice or container_id to be stopped. '
                             'If not provided it will use MICROSERVICE_NAME env variable.')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='Stop all matching services. By default only one instance is allowed to be stopped.')


def command_stop(args):
    microservice_handles = args.microservice_handle or [os.environ['MICROSERVICE_NAME']]
    if not microservice_handles:
        raise ValueError('No microservice name or container id supplied.')
    armada_utils.notify_about_detected_dev_environment(microservice_handles[0])

    services = {microservice_handle: armada_utils.get_matched_containers(microservice_handle)
                 for microservice_handle in microservice_handles}

    for microservice_handle, instances in six.iteritems(services):
        instances_count = len(instances)
        if instances_count > 1 and not args.all:
            raise armada_utils.ArmadaCommandException(
                'There are too many ({instances_count}) matching containers for service: {microservice_handle}. '
                'Provide more specific container_id or microservice name or use -a/--all flag.'.format(**locals()))

    were_errors = False
    for microservice_handle, instances in six.iteritems(services):
        instances_count = len(instances)
        if instances_count > 1:
            print('Stopping {instances_count} services {microservice_handle}...'.format(**locals()))
        else:
            microservice_name = instances[0]['ServiceName']
            container_id = instances[0]["ServiceID"].split(':')[0]
            print('Stopping service {microservice_name} ({container_id})...'.format(**locals()))

        for i, instance in enumerate(instances):
            try:
                if instances_count > 1:
                    print('[{0}/{1}]'.format(i + 1, instances_count))

                container_id = instance['ServiceID'].split(':')[0]
                payload = {'container_id': container_id}
                ship_name = instance['Address']
                result = armada_api.post('stop', payload, ship_name=ship_name)

                if result['status'] == 'error' and result['error'].startswith('armada API exception: ValueError - Cannot find ship:'):
                    payload['force'] = True
                    result = armada_api.post('stop', payload)

                if result['status'] == 'ok':
                    print('Service {container_id} has been stopped.'.format(**locals()))
                    print()
                else:
                    raise ArmadaCommandException('Stopping error: {0}'.format(result['error']))
            except:
                traceback.print_exc()
                were_errors = True

    if were_errors:
        sys.exit(1)
