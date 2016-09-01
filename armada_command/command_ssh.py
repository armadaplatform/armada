from __future__ import print_function

import argparse
import os
import pipes
import shlex

import armada_utils
import armada_api


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
    parser.add_argument('-l', '--local', default=False, action='store_true',
                        help='Limit services lookup to local ship.')


def prompt_select_instance(instances):
    print("There are multiple matching instances!")
    template = "\t{i}) {name} {address} {id} {status} {local}"
    for i, instance in enumerate(instances):
        if instance['address'] == 'n/a':
            continue
        local = "(local)" if armada_utils.is_local_container(instance['container_id']) else ""
        print(template.format(i=i+1, name=instance['name'], address=instance['address'], id=instance['container_id'],
                              status=instance['status'], local=local))
    try:
        selection = int(raw_input("Please select one: "))
        if 0 >= selection > len(instances):
            raise ValueError
    except ValueError:
        raise armada_utils.ArmadaCommandException("Invalid choice!")
    except KeyboardInterrupt:
        raise armada_utils.ArmadaCommandException("Aborted.")
    selection -= 1
    return instances[selection]


def command_ssh(args):
    microservice_name = args.microservice_name or os.environ['MICROSERVICE_NAME']
    if not microservice_name:
        raise ValueError('No microservice name supplied.')

    instances = armada_api.get_json('list', vars(args))

    instances_count = len(instances)
    if instances_count > 1:
        instance = prompt_select_instance(instances)
    else:
        instance = instances[0]

    if instance['address'] == 'n/a':
        raise armada_utils.ArmadaCommandException('Cannot connect to not running service.')

    container_id = instance['container_id']
    payload = {'container_id': container_id}

    is_local = armada_utils.is_local_container(container_id)

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
        print("Connecting to {0}...".format(instance['name']))
        ssh_args = shlex.split(docker_command)
    else:
        ssh_host = instance['address'].split(":")[0]
        docker_key_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'keys/docker.key')
        remote_ssh_chunk = 'ssh -t {tty} -p 2201 -i {docker_key_file} -o StrictHostKeyChecking=no docker@{ssh_host}' \
            .format(**locals())
        ssh_args = shlex.split(remote_ssh_chunk)
        ssh_args.extend(('sudo', docker_command))
        print("Connecting to {0} on host {1}...".format(instance['name'], ssh_host))

    os.execvp(ssh_args[0], ssh_args)
