import argparse
import os
import subprocess


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


def command_diagnose(args):
    microservice_name = args.microservice_name
    script = "diagnose.sh"
    if args.logs:
        script = "logs.sh"
    diagnostic_command = "armada ssh -i {microservice_name} bash < /opt/armada/armada_command/diagnostic_scripts/{script}".format(**locals())
    subprocess.call(diagnostic_command, shell=True)
