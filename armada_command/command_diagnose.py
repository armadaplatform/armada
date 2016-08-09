import argparse
import os
import subprocess
import json

from armada_command.consul import kv


def parse_args():
    parser = argparse.ArgumentParser(description='Performs diagnostic check on a microservice')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        default=os.environ.get('MICROSERVICE_NAME'),
                        help='Name of the microservice to diagnose. '
                             'If not provided it will use MICROSERVICE_NAME env variable. ')
    parser.add_argument('-l', '--logs', action='store_true', help='Displays last 10 lines from every log file.')
    parser.add_argument('-x', '--xx', action='store_true', help='Diagnose crashed/recovering/not-recovered.')


def command_diagnose(args):
    microservice_name = args.microservice_name
    if not args.xx:
        script = "diagnose.sh"
        if args.logs:
            script = "logs.sh"
        diagnostic_command = ("armada ssh -i {microservice_name} "
                              "bash < /opt/armada/armada_command/diagnostic_scripts/{script}").format(**locals())
        subprocess.call(diagnostic_command, shell=True)
    else:
        instances = kv.kv_list('service/{}/'.format(microservice_name))
        if instances is None:
            raise ArmadaCommandException('There are no microservice with name: {}'.format(microservice_name))
        instances_count = len(instances)
        if instances_count > 1:
            raise armada_utils.ArmadaCommandException(
                'There are too many ({instances_count}) matching containers. '
                'Provide more specific microservice name.'.format(**locals()))

        instance = instances[0]
        status = kv.kv_get(instance)['status']
        if status == 'recovering':
            params = kv.kv_get(instance)['params']
            print('RESTART_CONTAINER_PARAMETERS:')
            print(params)
        elif status == 'crashed':
            params = kv.kv_get(instance)['params']
            print('RESTART_CONTAINER_PARAMETERS:')
            print(json.dumps(params, indent=4, sort_keys=True))
            print('')
            container_id = kv.kv_get(instance)['container_id']
            print('Docker logs of container_id: {}'.format(container_id))
            diagnostic_command = ("docker logs {}".format(container_id))
            subprocess.call(diagnostic_command, shell=True)
