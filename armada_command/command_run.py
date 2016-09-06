from __future__ import print_function

import argparse
import os
import sys

import armada_api
from armada_command.armada_payload import RunPayload
from armada_command.armada_utils import ArmadaCommandException, is_verbose, is_ip, ship_ip_to_name
from armada_command.docker_utils.images import ArmadaImageFactory, select_latest_image, InvalidImagePathException
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import DOCKYARD_FALLBACK_ALIAS, get_default
from armada_command.ship_config import get_ship_config

CONFIG_PATH_BASE = '/etc/opt/'


def parse_args():
    parser = argparse.ArgumentParser(description='Run docker container with microservice.')
    add_arguments(parser)
    return parser.parse_args()


def are_we_in_vagrant():
    return os.path.exists('/etc/vagrant_box_build_time')


def _get_default_container_memory_limit():
    return get_ship_config().get('DEFAULT_CONTAINER_MEMORY_LIMIT')


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        help='Name of the microservice to be run. '
                             'If not provided it will use MICROSERVICE_NAME env variable. '
                             'You can also override default registry address, by passing full image path, '
                             'e.g. registry.docker.poollivepro.com:5000/example')
    parser.add_argument('--ship', metavar='SHIP_NAME',
                        help='Run microservice on specific ship (name or IP).')
    parser.add_argument('-d', '--dockyard',
                        help='Run image from dockyard with this alias. Use \'local\' to force using local repository.')
    parser.add_argument('-r', '--rename',
                        help='Renames the microservice upon starting new container.')

    parser.add_argument('-e', nargs='*', metavar='ENV_VAR', action='append',
                        help='Set environment variable inside the container. Formatted: "key=value"')
    parser.add_argument('-p', '--publish', nargs='*', metavar='PORT', action='append',
                        help='Publish additional container\'s ports to the host. '
                             'Formatted: host_port:container_port')
    parser.add_argument('-v', '--volumes', nargs='*', metavar='VOLUME', action='append',
                        help='Additional volumes for storage to be mounted to the container. '
                             'Formatted: "[host_path:]docker_path" '
                             'If host_path is not provided it will be the same as docker_path.')
    parser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')
    parser.add_argument('--hidden_vagrant_dev', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--hidden_is_restart', action='store_true', help=argparse.SUPPRESS)

    # vagrant only parameters
    if are_we_in_vagrant():
        parser.add_argument('-P', '--dynamic_ports', action='store_true',
                            help='Assign dynamic ports, even if run from inside of the vagrant.')
        parser.add_argument('--use_latest_image_code', action='store_true',
                            help='Use code from docker image instead of code from mounted dev directory '
                                 '(vagrant only).')

    # hermes parameters
    parser.add_argument('--env',
                        help='Name of environments (separated by ":") in which container will be run. '
                             'E.g. "production", "production/external", "dev/test:production" '
                             'If not provided it will use MICROSERVICE_ENV env variable.',
                        default=os.environ.get('MICROSERVICE_ENV'))
    parser.add_argument('--app_id',
                        help='Application or game for which this instance of microservice is dedicated. '
                             'It will be used to mount additional configs specific for that app/game.')
    parser.add_argument('-c', '--configs', nargs='*', metavar='CONFIG', action='append',
                        help='Additional paths to configs that will be mounted and added to CONFIG_PATH. '
                             'If it\'s a relative path it will be mounted from {}'.format(CONFIG_PATH_BASE))

    # Resource limit parameters
    parser.add_argument('--cpu-shares', help="CPU shares (relative weight)", type=int)
    parser.add_argument('--memory', help="Memory limit. Default: {}".format(_get_default_container_memory_limit()),
                        default=_get_default_container_memory_limit())
    parser.add_argument('--memory-swap', help="Total memory (memory + swap), '-1' to disable swap. "
                                              "Default: {}".format(_get_default_container_memory_limit()),
                        default=_get_default_container_memory_limit())
    parser.add_argument('--cgroup-parent', help="Optional parent cgroup for the container")


def warn_if_hit_crontab_environment_variable_length(env_variables_dict):
    for env_key, env_value in env_variables_dict.items():
        env_declaration = '{0}="{1}"'.format(env_key, env_value)
        if len(env_declaration) >= 1000:
            print('Warning: Environment variable {0} may have not been added to container\'s crontab because of '
                  'hitting 1000 characters crontab limit.'.format(env_key), file=sys.stderr)


def command_run(args):
    try:
        image = ArmadaImageFactory(args.microservice_name, 'local', os.environ.get('MICROSERVICE_NAME'))
    except InvalidImagePathException:
        raise ArmadaCommandException('ERROR: Please specify microservice_name argument'
                                     ' or set MICROSERVICE_NAME environment variable')
    ship = args.ship
    is_run_locally = ship is None
    dockyard_alias = args.dockyard or dockyard.get_dockyard_alias(image.image_name, is_run_locally)

    vagrant_dev = _is_vagrant_dev(args.hidden_vagrant_dev, dockyard_alias, image.image_name)

    dockyard_alias, image = _find_dockyard_with_image(vagrant_dev, args.hidden_is_restart, dockyard_alias,
                                                      image.image_name_with_tag)

    _print_run_info(image, dockyard_alias, ship, args.rename)

    payload = RunPayload()
    payload.update_image_path(image.image_path_with_tag)
    payload.update_dockyard(dockyard_alias)
    if vagrant_dev:
        payload.update_vagrant(args.dynamic_ports, args.publish, args.use_latest_image_code, image.image_name)
    payload.update_environment(args.e)
    payload.update_ports(args.publish)
    payload.update_volumes(args.volumes)
    payload.update_microservice_vars(args.rename, args.env, args.app_id)
    payload.update_run_command(vagrant_dev, args.env, image.image_name)
    payload.update_resource_limits(args.cpu_shares, args.memory, args.memory_swap, args.cgroup_parent)
    payload.update_configs(args.configs)

    if is_verbose():
        print('payload: {0}'.format(payload))

    warn_if_hit_crontab_environment_variable_length(payload.get('environment'))

    print('Checking if there is new image version. May take few minutes if download is needed...')
    result = armada_api.post('run', payload.data(), ship_name=ship)
    _handle_result(result, args.hidden_is_restart)


def _is_vagrant_dev(hidden_vagrant_dev, dockyard_alias, microservice_name):
    vagrant_dev = False
    if hidden_vagrant_dev or (are_we_in_vagrant() and dockyard_alias == 'local' and os.environ.get(
            'MICROSERVICE_NAME') == microservice_name):
        print('INFO: Detected development environment for microservice {microservice_name}. '
              'Using local docker registry.'.format(**locals()))
        vagrant_dev = True
    return vagrant_dev


def _find_dockyard_with_image(vagrant_dev, is_restart, dockyard_alias, microservice_name):
    image = ArmadaImageFactory(microservice_name, dockyard_alias)

    if vagrant_dev and is_restart:
        local_image = ArmadaImageFactory(image.image_name_with_tag, 'local')
        image = select_latest_image(image, local_image)
        if image == local_image:
            dockyard_alias = 'local'

    if vagrant_dev and not image.exists():
        print('Image {image} not found. Searching in default dockyard...'.format(**locals()))
        dockyard_alias = get_default()
        image = ArmadaImageFactory(image.image_name_with_tag, dockyard_alias)

    if not image.exists():
        if dockyard_alias == DOCKYARD_FALLBACK_ALIAS:
            was_fallback_dockyard = True
        else:
            print('Image {} not found. Searching in official Armada dockyard...'.format(image.image_name_with_tag))
            dockyard_alias = DOCKYARD_FALLBACK_ALIAS
            image = ArmadaImageFactory(image.image_name_with_tag, dockyard_alias)
            was_fallback_dockyard = False
        if was_fallback_dockyard or not image.exists():
            raise ArmadaCommandException('Image {} not found. Aborting.'.format(image.image_path_with_tag))

    return dockyard_alias, image


def _print_run_info(image, dockyard_alias, ship, rename):
    dockyard_string = image.dockyard.url or ''
    if dockyard_alias:
        dockyard_string += ' (alias: {dockyard_alias})'.format(**locals())

    ship_string = ' on remote ship: {ship}'.format(**locals()) if ship else ' locally'
    if rename:
        print('Running microservice {} (from image {}) from dockyard: {}{}...'.format(
            rename, image.image_name_with_tag, dockyard_string, ship_string))
    else:
        print('Running microservice {} from dockyard: {}{}...'.format(
            image.image_name_with_tag, dockyard_string, ship_string))


def _handle_result(result, is_restart):
    if not result:
        raise ArmadaCommandException("ERROR: armada API call failed.")

    if result.get('status') != 'ok':
        raise ArmadaCommandException('ERROR: {0}'.format(result['error']))

    container_id = result['container_id']
    if is_restart:
        print('Service has been restarted and is running in container {container_id} '
              'available at addresses:'.format(**locals()))
    else:
        print('Service is running in container {container_id} available at addresses:'.format(**locals()))
    for service_address, docker_port in result['endpoints'].iteritems():
        print('  {0} ({1})'.format(service_address, docker_port))
