from __future__ import print_function

import argparse
import os
import sys

import armada_api
from armada_command.armada_utils import ArmadaCommandException
from armada_command.docker_utils.images import ArmadaImage, select_latest_image
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import DOCKYARD_FALLBACK_ALIAS, get_default
from command_run_hermes import process_hermes, CONFIG_PATH_BASE

verbose = False


def parse_args():
    parser = argparse.ArgumentParser(description='Run docker container with microservice.')
    add_arguments(parser)
    return parser.parse_args()


def are_we_in_vagrant():
    return os.path.exists('/etc/vagrant_box_build_time')


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        default=os.environ.get('MICROSERVICE_NAME'),
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
                            help='Use code from docker image instead of code from mounted dev directory (vagrant only).')

    # hermes parameters
    parser.add_argument('--env',
                        help='Name of environments (separated by ":") in which container will be run. '
                             'E.g. "production", "production/external", "dev/test:production"')
    parser.add_argument('--app_id',
                        help='Application or game for which this instance of microservice is dedicated. '
                             'It will be used to mount additional configs specific for that app/game.')
    parser.add_argument('-c', '--configs', nargs='*', metavar='CONFIG', action='append',
                        help='Additional paths to configs that will be mounted and added to CONFIG_PATH. '
                             'If it\'s a relative path it will be mounted from {config_path_base}'.format(
                            config_path_base=CONFIG_PATH_BASE))

    # Docker args
    parser.add_argument('--cpu-shares', help="CPU shares (relative weight)", type=int)
    parser.add_argument('--memory', help="Memory limit")
    parser.add_argument('--memory-swap', help="Total memory (memory + swap), '-1' to disable swap")
    parser.add_argument('--cgroup-parent', help="Optional parent cgroup for the container")


def warn_if_hit_crontab_environment_variable_length(env_variables_dict):
    for env_key, env_value in env_variables_dict.items():
        env_declaration = '{0}="{1}"'.format(env_key, env_value)
        if len(env_declaration) >= 1000:
            print(
                'Warning: Environment variable {0} may have not been added to container\'s crontab because of hitting '
                '1000 characters crontab limit.'.format(env_key), file=sys.stderr)


def command_run(args):
    if args.verbose:
        global verbose
        verbose = True
    microservice_name = args.microservice_name
    if not microservice_name:
        raise ArmadaCommandException('ERROR: Please specify microservice_name argument'
                                     ' or set MICROSERVICE_NAME environment variable')

    ship = args.ship
    is_run_locally = ship is None
    dockyard_alias = args.dockyard or dockyard.get_dockyard_alias(microservice_name, is_run_locally)
    vagrant_dev = False
    if args.hidden_vagrant_dev or (are_we_in_vagrant() and dockyard_alias == 'local'):
        print('INFO: Detected development environment for microservice {microservice_name}. '
              'Using local docker registry.'.format(**locals()))
        vagrant_dev = True
    image = ArmadaImage(microservice_name, dockyard_alias)

    if args.hidden_is_restart:
        local_image = ArmadaImage(image.image_name, 'local')
        image = select_latest_image(image, local_image)

    if vagrant_dev and not image.exists():
        print('Image {image} not found. Searching in default dockyard...'.format(**locals()))
        dockyard_alias = get_default()
        image = ArmadaImage(microservice_name, dockyard_alias)

    if not image.exists():
        if dockyard_alias == DOCKYARD_FALLBACK_ALIAS:
            was_fallback_dockyard = True
        else:
            print('Image {image} not found. Searching in official Armada dockyard...'.format(**locals()))
            dockyard_alias = DOCKYARD_FALLBACK_ALIAS
            image = ArmadaImage(microservice_name, dockyard_alias)
            was_fallback_dockyard = False
        if was_fallback_dockyard or not image.exists():
            print('Image {image} not found. Aborting.'.format(**locals()))
            sys.exit(1)

    dockyard_string = image.dockyard.url or ''
    if dockyard_alias:
        dockyard_string += ' (alias: {dockyard_alias})'.format(**locals())
    ship_string = ' on remote ship: {ship}'.format(**locals()) if ship else ' locally'
    if args.rename:
        print('Running microservice {} (from image {}) from dockyard: {}{}...'.format(
            args.rename, image.image_name, dockyard_string, ship_string))
    else:
        print('Running microservice {} from dockyard: {}{}...'.format(
            image.image_name, dockyard_string, ship_string))

    payload = {'image_path': image.image_path, 'environment': {}, 'ports': {}, 'volumes': {}}
    if dockyard_alias and dockyard_alias != 'local':
        dockyard_info = dockyard.alias.get_alias(dockyard_alias)
        if not dockyard_info:
            raise ArmadaCommandException("Couldn't read configuration for dockyard alias {0}.".format(dockyard_alias))
        payload['dockyard_user'] = dockyard_info.get('user')
        payload['dockyard_password'] = dockyard_info.get('password')

    if vagrant_dev:
        if not (args.dynamic_ports or args.publish):
            payload['ports']['4999'] = '80'
        if not args.use_latest_image_code:
            microservice_path = '/opt/{microservice_name}'.format(**locals())
            payload['volumes'][microservice_path] = microservice_path
        payload['environment']['ARMADA_VAGRANT_DEV'] = '1'

    hermes_env, hermes_volumes = process_hermes(image.image_name, args.env, args.app_id,
                                                sum(args.configs or [], []))
    payload['environment'].update(hermes_env or {})
    payload['volumes'].update(hermes_volumes or {})

    # --- environment
    for env_var in sum(args.e or [], []):
        env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
        payload['environment'][env_key] = env_value

    # --- ports
    for port_mapping in sum(args.publish or [], []):
        try:
            port_host, port_container = map(int, (port_mapping.split(':', 1) + [None])[:2])
            payload['ports'][str(port_host)] = str(port_container)
        except (ValueError, TypeError):
            print('Invalid port mapping: {0}'.format(port_mapping), file=sys.stderr)
            return

    # --- volumes
    for volume_string in sum(args.volumes or [], []):
        volume = volume_string.split(':')
        if len(volume) == 1:
            volume *= 2
        payload['volumes'][volume[0]] = volume[1]

    # --- name
    payload['microservice_name'] = args.rename

    # --- run_arguments
    run_command = 'armada ' + ' '.join(sys.argv[1:])
    if vagrant_dev and '--hidden_vagrant_dev' not in run_command:
        run_command += ' --hidden_vagrant_dev'
    if '--hidden_is_restart' not in run_command:
        run_command += ' --hidden_is_restart'
    payload['run_command'] = run_command

    # --- docker_args
    resource_limits = {}
    if args.cpu_shares:
        resource_limits['cpu_shares'] = args.cpu_shares
    if args.memory:
        resource_limits['memory'] = args.memory
    if args.memory_swap:
        resource_limits['memory_swap'] = args.memory_swap
    if args.cgroup_parent:
        resource_limits['cgroup_parent'] = args.cgroup_parent
    payload['resource_limits'] = resource_limits

    # ---
    if verbose:
        print('payload: {0}'.format(payload))

    warn_if_hit_crontab_environment_variable_length(payload['environment'])
    print('Checking if there is new image version. May take few minutes if download is needed...')
    result = armada_api.post('run', payload, ship_name=ship)

    if result['status'] == 'ok':
        container_id = result['container_id']
        if args.hidden_is_restart:
            print('Service has been restarted and is running in container {container_id} '
                  'available at addresses:'.format(**locals()))
        else:
            print('Service is running in container {container_id} available at addresses:'.format(**locals()))
        for service_address, docker_port in result['endpoints'].iteritems():
            print('  {0} ({1})'.format(service_address, docker_port))
    else:
        print('ERROR: {0}'.format(result['error']))
        sys.exit(1)
