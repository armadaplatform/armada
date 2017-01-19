from __future__ import print_function

import os
import pwd
import socket

from armada_command.armada_utils import ArmadaCommandException, execute_local_command
from armada_command.docker_utils.compatibility import docker_backend
from armada_command.docker_utils.images import ArmadaImageFactory, InvalidImagePathException
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import print_http_dockyard_unavailability_warning
from armada_command.dockyard.dockyard import dockyard_factory


def add_arguments(parser):
    parser.add_argument('image_path',
                        nargs='?',
                        help='Name of the image to be pushed. '
                             'If not provided it will use MICROSERVICE_NAME env variable.'
                             'You can also override default registry address, by passing full image path,  '
                             'e.g. dockyard.example.com:5000/my-service')
    parser.add_argument('-d', '--dockyard',
                        help='Push image to dockyard with this alias.')


def login_to_dockyard(dockyard_alias):
    dockyard_dict = dockyard.get_dockyard_dict(dockyard_alias)
    if not dockyard_dict:
        raise ArmadaCommandException("Couldn't read configuration for dockyard alias {0}.".format(dockyard_alias))

    dockyard_user = dockyard_dict.get('user')
    dockyard_password = dockyard_dict.get('password')
    if dockyard_user and dockyard_password:
        dockyard_address = dockyard_dict.get('address')
        current_user_email = '{0}@{1}'.format(pwd.getpwuid(os.getuid()).pw_name, socket.gethostname())
        login_command = ('docker login --username="{dockyard_user}" --password="{dockyard_password}" '
                         '--email="{current_user_email}" {dockyard_address}').format(**locals())
        if execute_local_command(login_command)[0] != 0:
            raise ArmadaCommandException(
                'ERROR: Could not login to dockyard with alias {dockyard_alias}.'.format(**locals()))


def command_push(args):
    try:
        source_image = ArmadaImageFactory(args.image_path, 'local', os.environ.get('MICROSERVICE_NAME'))
    except InvalidImagePathException:
        raise ArmadaCommandException('ERROR: Please specify image_path argument'
                                     ' or set MICROSERVICE_NAME environment variable')
    dockyard_alias = args.dockyard
    if not source_image.dockyard_address:
        if not source_image.exists():
            raise Exception('Image {} does not exist. Typo?'.format(source_image.image_name_with_tag))
        destination_image = ArmadaImageFactory(source_image.image_name_with_tag, dockyard_alias)
        dockyard_string = destination_image.dockyard.url or ''
        dockyard_string += ' (alias: {})'.format(dockyard_alias) if dockyard_alias else ''
        print('Pushing image {} to dockyard: {}...'.format(source_image.image_name_with_tag, dockyard_string))
        tag_command = docker_backend.build_tag_command(source_image.image_name_with_tag,
                                                       destination_image.image_path_with_tag)
        print(tag_command)
        assert execute_local_command(tag_command, stream_output=True, retries=1)[0] == 0
    else:
        # If command was called with [docker_registry_address]/[image_name] and no -d/--dockyard, then simply
        # mimic 'docker push' behavior (without tagging).
        print('Pushing image {}...'.format(source_image.image_path_with_tag))
        destination_image = source_image

    dockyard_dict = dockyard.get_dockyard_dict(dockyard_alias)
    did_print = False
    d = dockyard_factory(dockyard_dict.get('address'), dockyard_dict.get('user'), dockyard_dict.get('password'))
    if d.is_http():
        did_print = print_http_dockyard_unavailability_warning(
            dockyard_dict['address'],
            dockyard_alias,
            "ERROR! Cannot push to dockyard!",
        )

    retries = 0 if did_print else 3
    login_to_dockyard(dockyard_alias)
    push_command = 'docker push {}'.format(destination_image.image_path_with_tag)
    assert execute_local_command(push_command, stream_output=True, retries=retries)[0] == 0
