from __future__ import print_function

import argparse
import os
import sys

from armada_command.armada_utils import execute_local_command, is_verbose
from armada_command.docker_utils.images import ArmadaImage
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import DOCKYARD_FALLBACK_ALIAS, print_http_dockyard_unavailability_warning
from armada_command.dockyard.dockyard import dockyard_factory


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


def _get_base_image_name():
    with open('Dockerfile') as dockerfile:
        for line in dockerfile:
            if line.startswith('FROM '):
                return line.split()[1]


def command_build(args):
    microservice_name = args.microservice_name or os.environ.get('MICROSERVICE_NAME')
    if not microservice_name:
        raise ValueError('No microservice name supplied.')
    if not os.path.exists('Dockerfile'):
        print('ERROR: Dockerfile not found in current directory', file=sys.stderr)
        return
    base_image_name = _get_base_image_name()
    dockyard_alias = args.dockyard or dockyard.get_dockyard_alias(base_image_name, is_run_locally=True)

    base_image = ArmadaImage(base_image_name, dockyard_alias)

    if base_image.is_remote():
        if not base_image.exists():
            if dockyard_alias == DOCKYARD_FALLBACK_ALIAS:
                was_fallback_dockyard = True
            else:
                print('Base image {base_image} not found. Searching in official Armada dockyard...'.format(**locals()))
                dockyard_alias = DOCKYARD_FALLBACK_ALIAS
                base_image = ArmadaImage(base_image_name, dockyard_alias)
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
        base_image_path = base_image.image_path
        if is_verbose():
            print('Fetching base image: "{base_image_path}".\n'.format(**locals()))

        pull_command = 'docker pull {base_image_path}'.format(**locals())

        assert execute_local_command(pull_command, stream_output=True, retries=retries)[0] == 0
        if base_image_path != base_image_name:
            if is_verbose():
                print('Tagging "{base_image_path}" as "{base_image_name}"\n'.format(**locals()))
            tag_command = 'docker tag -f {base_image_path} {base_image_name}'.format(**locals())
            assert execute_local_command(tag_command, stream_output=True, retries=1)[0] == 0

    build_command = 'docker build -t {microservice_name} .'.format(**locals())
    assert execute_local_command(build_command, stream_output=True)[0] == 0
