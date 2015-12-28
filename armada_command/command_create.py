from __future__ import print_function
import os
import argparse
import tempfile
import shutil

from armada_command.armada_utils import execute_local_command, ArmadaCommandException
from armada_command.dockyard import dockyard


def parse_args():
    parser = argparse.ArgumentParser(description='Create skeleton for new microservice.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('name',
                        help='Name of the created microservice.')
    parser.add_argument('-b', '--base-template', default='python',
                        help='Base microservice template. Possible choices: python, python3, node')


def _replace_in_file_content(file_path, old, new):
    with open(file_path) as f:
        content = f.read()
    content = content.replace(old, new)
    with open(file_path, 'w') as f:
        f.write(content)


def _replace_in_path(path, old, new):
    for subpath, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            file_path = os.path.join(subpath, file_name)
            _replace_in_file_content(file_path, old, new)
            if old in file_name:
                new_file_path = file_path.replace(old, new)
                shutil.move(file_path, new_file_path)


def _get_template_name(base):
    return "microservice_{base}_template".format(**locals())


def command_create(args):
    base_template = _get_template_name(args.base_template)
    service_name = args.name or base_template
    destination_dir = os.path.join(os.getcwd(), service_name)
    if os.path.exists(destination_dir):
        raise ArmadaCommandException('Destination dir {destination_dir} already exists.'.format(**locals()))
    command_list_code, command_list_out, command_list_err = execute_local_command('armada list armada -q | head -1')

    if command_list_code != 0:
        raise ArmadaCommandException('Could not get Armada container id:\n{command_list_err}'.format(**locals()))
    path_to_base_template = os.path.join('/opt/templates', base_template)
    armada_container_id = command_list_out.strip()
    temp_dir = tempfile.mkdtemp()
    try:
        command_cp = 'docker cp {armada_container_id}:{path_to_base_template} {temp_dir}'.format(**locals())
        command_cp_code, command_cp_out, command_cp_err = execute_local_command(command_cp)
        if command_cp_code != 0:
            raise ArmadaCommandException('Could not get microservice template:\n{command_cp_err}'.format(**locals()))
        shutil.move(os.path.join(temp_dir, base_template), destination_dir)
        if service_name != base_template:
            upper_template = base_template.upper()
            template_name_variable = '_{upper_template}_'.format(**locals())
            _replace_in_path(destination_dir, template_name_variable, service_name)
        dockyard_address = dockyard.get_dockyard_address()
        template_dockyard_variable = '_DOCKYARD_ADDRESS_'
        _replace_in_path(destination_dir, template_dockyard_variable, dockyard_address)

        print('Service {service_name} has been created in {destination_dir} from {args.base_template} template.'
              .format(**locals()))
    finally:
        shutil.rmtree(temp_dir)
