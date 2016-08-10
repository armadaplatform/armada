from __future__ import print_function

import argparse
import os
import pipes
import shlex

import armada_utils
from armada_command.consul.consul import consul_query


def parse_args():
    parser = argparse.ArgumentParser(description='ssh into docker container.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('microservice_name', nargs='?',
                        help='Name of the microservice or container_id to ssh into. '
                             'If not provided it will use MICROSERVICE_NAME env variable.')
    parser.add_argument('command', nargs=argparse.REMAINDER,
                        help='Execute command inside the container. '
                             'If not provided it will create interactive bash terminal.')
    parser.add_argument('-t', '--tty', default=False, action='store_true',
                        help='Allocate a pseudo-TTY.')
    parser.add_argument('-i', '--interactive', default=False, action='store_true',
                        help='Keep STDIN open even if not attached.')


def command_ssh(args):
    microservice_name = args.microservice_name or os.environ['MICROSERVICE_NAME']
    if not microservice_name:
        raise ValueError('No microservice name supplied.')

    instances = armada_utils.get_matched_containers(microservice_name)
    instances_count = len(instances)
    if instances_count > 1:
        raise armada_utils.ArmadaCommandException(
            'There are too many ({instances_count}) matching containers. '
            'Provide more specific container_id or microservice name.'.format(**locals()))
    instance = instances[0]

    service_id = instance['ServiceID']
    container_id = service_id.split(':')[0]
    if container_id.startswith('kv_'):
        raise armada_utils.ArmadaCommandException('Cannot connect to not running service.')
    payload = {'container_id': container_id}

    is_local = False
    local_microservices_ids = set(consul_query('agent/services').keys())
    if container_id in local_microservices_ids:
        is_local = True

    if args.command:
        command = ' '.join(args.command)
    else:
        command = 'bash'
        args.tty = True
        args.interactive = True

    tty = '-t' if args.tty else ''
    interactive = '-i' if args.interactive else ''
    term = os.environ.get('TERM') or 'dummy'

    command = pipes.quote(command)
    docker_command = 'docker exec {interactive} {tty} {container_id} env TERM={term} ' \
                     'sh -c {command}'.format(**locals())

    if is_local:
        print("Connecting to {0}...".format(instance['ServiceName']))
        ssh_args = shlex.split(docker_command)
    else:
        ssh_host = instance['Address']
        docker_key_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'keys/docker.key')
        remote_ssh_chunk = 'ssh -t {tty} -p 2201 -i {docker_key_file} -o StrictHostKeyChecking=no docker@{ssh_host}' \
            .format(**locals())
        ssh_args = shlex.split(remote_ssh_chunk)
        ssh_args.extend(('sudo', docker_command))
        print("Connecting to {0} on host {1}...".format(instance['ServiceName'], ssh_host))

    os.execvp(ssh_args[0], ssh_args)
