from __future__ import print_function

import argparse
import os
import pipes
import shlex

import armada_utils


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
                        help='Limit matching services lookup to local ship.')
    parser.add_argument('--no-prompt', default=False, action='store_true',
                        help="Don't prompt. Command fails if multiple matching services are found.")


def prompt_select_instance(instances):
    print("There are multiple matching instances!")
    template = "\t{i}) {name} {address}:{port} {id} {local}"
    for i, instance in enumerate(instances):
        local = "(local)" if armada_utils.is_local_container(instance['ServiceID']) else ""
        print(template.format(i=i + 1, name=instance['ServiceName'], address=instance['Address'],
                              port=instance['ServicePort'], id=instance['ServiceID'], local=local))
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

    instances = [i for i in armada_utils.get_matched_containers(microservice_name) if 'Status' not in i]

    if args.local:
        instances = [i for i in instances if armada_utils.is_local_container(i['ServiceID'])]

    instances_count = len(instances)

    if instances_count < 1:
        raise armada_utils.ArmadaCommandException(
            'There are no running containers with microservice: '
            '{microservice_name}'.format(**locals()))

    if instances_count > 1:
        if args.no_prompt:
            raise armada_utils.ArmadaCommandException(
                'There are too many ({instances_count}) matching containers. '
                'Provide more specific container_id or microservice name.'.format(**locals()))
        instance = prompt_select_instance(instances)
    else:
        instance = instances[0]

    if 'Status' in instance:
        raise armada_utils.ArmadaCommandException('Cannot connect to not running service.')

    service_id = instance['ServiceID']
    container_id = service_id.split(':')[0]
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
