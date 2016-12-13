from __future__ import print_function

import argparse
import os
import sys

from armada_command.armada_utils import execute_local_command, is_verbose
from armada_command.docker_utils.compatibility import docker_backend
from armada_command.docker_utils.images import ArmadaImageFactory, InvalidImagePathException
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import DOCKYARD_FALLBACK_ALIAS, print_http_dockyard_unavailability_warning
from armada_command.dockyard.dockyard import dockyard_factory
from armada_utils import ArmadaCommandException


def parse_args():
    parser = argparse.ArgumentParser(description='build armada image')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('microservice_name', nargs='?',
                        help='Name of the microservice to be built. '
                             'If not provided it will use MICROSERVICE_NAME env variable.')
    parser.add_argument('-d', '--dockyard',
                        help='Build from image from dockyard with this alias. '
                             "Use 'local' to force using local repository.")
    parser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')
    parser.add_argument('-s', '--squash', action='store_true', help='Squash image. Does not work with -f/--file.')
    parser.add_argument('-f', '--file', default='Dockerfile',
                        help='Path to the Dockerfile. Does not work with -s/--squash.')


def _get_base_image_name(dockerfile_path):
    with open(dockerfile_path) as dockerfile:
        for line in dockerfile:
            if line.startswith('FROM '):
                return line.split()[1]


def command_build(args):
    dockerfile_path = args.file
    if args.squash:
        if dockerfile_path != 'Dockerfile':
            raise ArmadaCommandException('You cannot use -f/--file flag together with -s/--squash.')
        chain_run_commands()

    if not os.path.exists(dockerfile_path):
        print('ERROR: {} not found.'.format(dockerfile_path), file=sys.stderr)
        return

    base_image_name = _get_base_image_name(dockerfile_path)
    dockyard_alias = args.dockyard or dockyard.get_dockyard_alias(base_image_name, is_run_locally=True)

    try:
        image = ArmadaImageFactory(args.microservice_name, dockyard_alias, os.environ.get('MICROSERVICE_NAME'))
    except InvalidImagePathException:
        raise ValueError('No microservice name supplied.')

    base_image = ArmadaImageFactory(base_image_name, dockyard_alias)
    if base_image.is_remote():
        if not base_image.exists():
            if dockyard_alias == DOCKYARD_FALLBACK_ALIAS:
                was_fallback_dockyard = True
            else:
                print('Base image {base_image} not found. Searching in official Armada dockyard...'.format(**locals()))
                dockyard_alias = DOCKYARD_FALLBACK_ALIAS
                base_image = ArmadaImageFactory(base_image_name, dockyard_alias)
                was_fallback_dockyard = False
            if was_fallback_dockyard or not base_image.exists():
                print('Base image {base_image} not found. Aborting.'.format(**locals()))
                sys.exit(1)
        dockyard_dict = dockyard.get_dockyard_dict(dockyard_alias)
        did_print = False
        d = dockyard_factory(dockyard_dict.get('address'), dockyard_dict.get('user'), dockyard_dict.get('password'))
        if d.is_http():
            did_print = print_http_dockyard_unavailability_warning(
                dockyard_dict['address'],
                dockyard_alias,
                "ERROR! Cannot pull from dockyard!",
            )
        retries = 0 if did_print else 3
        base_image_path = base_image.image_path_with_tag
        if is_verbose():
            print('Fetching base image: "{base_image_path}".\n'.format(**locals()))

        pull_command = 'docker pull {base_image_path}'.format(**locals())

        assert execute_local_command(pull_command, stream_output=True, retries=retries)[0] == 0
        if base_image_path != base_image_name:
            if is_verbose():
                print('Tagging "{base_image_path}" as "{base_image_name}"\n'.format(**locals()))
            tag_command = docker_backend.build_tag_command(base_image_path, base_image_name)
            assert execute_local_command(tag_command, stream_output=True, retries=1)[0] == 0

    build_command = 'docker build -f {} -t {} .'.format(dockerfile_path, image.image_name_with_tag)
    assert execute_local_command(build_command, stream_output=True)[0] == 0

    if args.squash:
        os.rename('Dockerfile.tmp', 'Dockerfile')
        squash_command = 'docker-squash {} -t {}'.format(image.image_name_with_tag,
                                                         image.image_name_with_tag)
        assert execute_local_command(squash_command, stream_output=True)[0] == 0


def _join_commands(run_commands):
    chained_run = 'RUN ' + ' && '.join(run_commands)
    if 'apt-get' in chained_run and 'apt-get clean' not in chained_run:
        chained_run += ' && apt-get clean && rm -rf /var/lib/apt/lists/*'
    chained_run += '\n'
    return chained_run


def chain_run_commands():
    new_dockerfile_commands = []
    run_commands = []
    with open('Dockerfile') as dockerfile:
        join_next_line = False
        for line in dockerfile:
            if line == '\n' or line.startswith('#'):
                continue
            elif join_next_line or line.startswith('RUN'):
                striped = line[4:].strip() if line.startswith('RUN') else line.strip()
                if striped.endswith('\\'):
                    join_next_line = True
                    striped = striped[:-1].strip().strip('&')
                else:
                    join_next_line = False
                run_commands.append(striped)
            else:
                join_next_line = False
                new_dockerfile_commands.append(line)
        if run_commands:
            chained_run = _join_commands(run_commands)
            new_dockerfile_commands.append(chained_run)
    dockerfile.close()
    os.rename('Dockerfile', 'Dockerfile.tmp')
    with open('Dockerfile', 'w') as dockerfile:
        for line in new_dockerfile_commands:
            dockerfile.write(line)
