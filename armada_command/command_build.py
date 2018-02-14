from __future__ import print_function

import os

from armada_command.armada_utils import ArmadaCommandException, execute_local_command, is_verbose, \
    notify_about_detected_dev_environment
from armada_command.docker_utils.images import ArmadaImageFactory, InvalidImagePathException
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import DOCKYARD_FALLBACK_ALIAS, print_http_dockyard_unavailability_warning
from armada_command.dockyard.dockyard import dockyard_factory, get_default_alias


def add_arguments(parser):
    parser.add_argument('microservice_name', nargs='?',
                        help='Name of the microservice to be built. '
                             'If not provided it will use MICROSERVICE_NAME env variable.')
    parser.add_argument('--build-arg', action='append', help='Set build-time variables', default=[])
    parser.add_argument('-d', '--dockyard',
                        help='Build from image from dockyard with this alias. '
                             "Use 'local' to force using local repository.")
    parser.add_argument('-s', '--squash', action='store_true', help='Squash image. Does not work with --file.')
    parser.add_argument('--file', default='Dockerfile',
                        help='Path to the Dockerfile. Does not work with -s/--squash.')


def _get_base_image_names(dockerfile_path):
    result = []
    with open(dockerfile_path) as dockerfile:
        for line in dockerfile:
            if line.startswith('FROM '):
                result.append(line.split()[1])
    return result


def command_build(args):
    dockerfile_path = args.file
    if not os.path.exists(dockerfile_path):
        raise ArmadaCommandException('ERROR: {} not found.'.format(dockerfile_path))

    base_image_names = _get_base_image_names(dockerfile_path)
    dockyard_alias = args.dockyard or get_default_alias()

    try:
        image = ArmadaImageFactory(args.microservice_name, dockyard_alias, os.environ.get('MICROSERVICE_NAME'))
    except InvalidImagePathException:
        raise ArmadaCommandException('No microservice name supplied.')

    notify_about_detected_dev_environment(image.image_name)

    for base_image_name in base_image_names:
        base_image = ArmadaImageFactory(base_image_name, args.dockyard)
        if base_image.is_remote():
            if not base_image.exists():
                if dockyard_alias == DOCKYARD_FALLBACK_ALIAS:
                    was_fallback_dockyard = True
                else:
                    print('Base image {base_image} not found. '
                          'Searching in official Armada dockyard...'.format(**locals()))
                    dockyard_alias = DOCKYARD_FALLBACK_ALIAS
                    base_image = ArmadaImageFactory(base_image_names, dockyard_alias)
                    was_fallback_dockyard = False
                if was_fallback_dockyard or not base_image.exists():
                    raise ArmadaCommandException('Base image {base_image} not found. Aborting.'.format(**locals()))
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
            if base_image_path != base_image_names:
                if is_verbose():
                    print('Tagging "{base_image_path}" as "{base_image_names}"\n'.format(**locals()))

                tag_command = "docker tag {} {}".format(base_image_path, base_image_names)
                assert execute_local_command(tag_command, stream_output=True, retries=1)[0] == 0

    build_command = _generate_build_command(args, dockerfile_path, image)
    assert execute_local_command(' '.join(build_command), stream_output=True)[0] == 0


def _generate_build_command(command_args, dockerfile_path, image):
    build_command = ['docker',
                     'build',
                     '-f', dockerfile_path,
                     '-t', image.image_name_with_tag,
                     ]

    if command_args.squash:
        build_command.append('--squash')
    for build_arg in command_args.build_arg:
        build_command += ['--build-arg', build_arg]

    build_command.append('.')
    return build_command
