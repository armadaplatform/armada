from __future__ import print_function
import argparse
import os
import pwd
import socket

from armada_command.armada_utils import ArmadaCommandException, execute_local_command
from armada_command.docker_utils.images import ArmadaImage
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import print_dockyard_unavailability_warning

def parse_args():
    parser = argparse.ArgumentParser(description='push armada image to dockyard')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        default=os.environ.get('MICROSERVICE_NAME'),
                        help='Name of the microservice to be pushed. '
                             'If not provided it will use MICROSERVICE_NAME env variable.'
                             'You can also override default registry address, by passing full image path,  '
                             'e.g. registry.docker.poollivepro.com:5000/example')
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
        login_command = 'docker login --username="{dockyard_user}" --password="{dockyard_password}" --email="{current_user_email}" {dockyard_address}'.format(**locals())
        if execute_local_command(login_command)[0] != 0:
            raise ArmadaCommandException('ERROR: Could not login to dockyard with alias {dockyard_alias}.'.format(**locals()))


def command_push(args):
    image_name = args.microservice_name
    if not image_name:
        raise ArmadaCommandException('ERROR: Please specify microservice_name argument'
                                     ' or set MICROSERVICE_NAME environment variable')
    dockyard_alias = args.dockyard
    image = ArmadaImage(image_name, dockyard_alias)

    if '/' not in image_name:
        if not ArmadaImage(image.microservice_name, 'local').exists():
            raise Exception('Image {image.microservice_name} does not exist. Typo?'.format(**locals()))
        dockyard_string = image.dockyard_address or ''
        dockyard_string += ' (alias: {dockyard_alias})'.format(**locals()) if dockyard_alias else ''
        print('Pushing microservice {image.microservice_name} to dockyard: {dockyard_string}...'.format(
            **locals()))
        tag_command = 'docker tag -f {image.microservice_name} {image.image_path}'.format(**locals())
        assert execute_local_command(tag_command, stream_output=True, retries=1)[0] == 0
    else:
        # If command was called with [docker_registry_address]/[microservice_name] and no -d/--dockyard, then simply
        # mimic 'docker push' behavior (without tagging).
        print('Pushing image {image}...'.format(**locals()))

    dockyard_dict = dockyard.get_dockyard_dict(dockyard_alias)
    did_print = print_dockyard_unavailability_warning(dockyard_dict.get("address"),
                                dockyard_dict.get("user"),
                                dockyard_dict.get("password"),
                                "ERROR! Cannot push to dockyard!")
    retries = 0 if did_print else 3
    login_to_dockyard(dockyard_alias)
    push_command = 'docker push {image.image_path}'.format(**locals())
    assert execute_local_command(push_command, stream_output=True, retries=retries)[0] == 0
