import os
import subprocess

from armada_utils import get_matched_containers

from armada_command.scripts.compat import json


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        default=os.environ.get('MICROSERVICE_NAME'),
                        help='Name of the microservice to diagnose. '
                             'If not provided it will use MICROSERVICE_NAME env variable. ')
    parser.add_argument('-l', '--logs', action='store_true', help='Displays last 10 lines from every log file.')


def command_diagnose(args):
    microservice_name = args.microservice_name

    script = "diagnose.sh"
    if args.logs:
        script = "logs.sh"
    diagnostic_command = ("armada ssh -i {microservice_name} "
                          "bash < /opt/armada/armada_command/diagnostic_scripts/{script}").format(**locals())
    exit_code = subprocess.call(diagnostic_command, shell=True)
    if exit_code != 0:
        instances = get_matched_containers(microservice_name)
        if instances is not None and len(instances) == 1:
            instance = instances[0]
            status = instance['Status']
            if status == 'recovering':
                params = instance['params']
                print('RESTART_CONTAINER_PARAMETERS:')
                print(json.dumps(params, indent=4, sort_keys=True))
            elif status in ['crashed', 'not-recovered']:
                params = instance['params']
                print('RESTART_CONTAINER_PARAMETERS:')
                print(json.dumps(params, indent=4, sort_keys=True))
                print('')
                container_id = instance['container_id']
                print('Docker logs of container_id: {}'.format(container_id))
                diagnostic_command = ("docker logs {}".format(container_id))
                subprocess.call(diagnostic_command, shell=True)
