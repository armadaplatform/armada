from __future__ import print_function
import argparse
import base64
import json
import os
import sys
import traceback

import armada_api
import armada_utils


def parse_args():
    parser = argparse.ArgumentParser(description='Restart running docker containers.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('microservice_name', nargs='?',
                        help='Name of the microservice or container_id to be restarted. '
                             'If not provided it will use MICROSERVICE_NAME env variable.')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='Restart all matching services. By default only one instance is allowed to be restarted.')
    parser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')


def command_restart(args):
    if args.verbose:
        global verbose
        verbose = True
    microservice_name = args.microservice_name or os.environ['MICROSERVICE_NAME']
    if not microservice_name:
        raise ValueError('No microservice name supplied.')

    instances = armada_utils.get_matched_containers(microservice_name)

    instances_count = len(instances)

    if instances_count > 1:
        if not args.all:
            raise armada_utils.ArmadaCommandException(
                'There are too many ({instances_count}) matching containers. '
                'Provide more specific container_id or microservice name or use -a/--all flag.'.format(**locals()))
        print('Restarting {instances_count} services {microservice_name}...'.format(**locals()))
    else:
        print('Restarting service {microservice_name}...'.format(**locals()))

    were_errors = False
    for i, instance in enumerate(instances):
        try:
            if instances_count > 1:
                print('[{0}/{1}]'.format(i + 1, instances_count))
            container_id = instance['ServiceID'].split(':')[0]
            is_run_locally = armada_utils.is_local_container(container_id)
            if is_run_locally:
                result = json.loads(armada_api.get('env/{container_id}/ARMADA_RUN_COMMAND'.format(**locals())))
                if result['status'] == 'ok':
                    stop_command = 'armada stop {container_id}'.format(**locals())
                    run_command = base64.b64decode(result['value'])
                    assert armada_utils.execute_local_command(stop_command, stream_output=True, retries=3)[0] == 0
                    assert armada_utils.execute_local_command(run_command, stream_output=True, retries=5)[0] == 0
                    if instances_count > 1:
                        print()
                else:
                    raise armada_utils.ArmadaCommandException('ERROR: {0}'.format(result['error']))
            else:
                payload = {'container_id': container_id}

                result = armada_api.post('restart', payload, ship_name=instance['Node'])

                if result['status'] == 'ok':
                    new_container_id = result['container_id']
                    print('Service has been restarted and is running in container {new_container_id} '
                          'available at addresses:'.format(**locals()))
                    for service_address, docker_port in result['endpoints'].iteritems():
                        print('  {0} ({1})'.format(service_address, docker_port))
                    if instances_count > 1:
                        print()
                else:
                    raise armada_utils.ArmadaCommandException('ERROR: {0}'.format(result['error']))
        except:
            traceback.print_exc()
            were_errors = True
    if were_errors:
        sys.exit(1)