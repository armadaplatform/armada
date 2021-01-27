import argparse
import json
import os
import sys
import traceback

from requests.packages import urllib3

from armada_command import armada_api
from armada_command import command_build
from armada_command import command_create
from armada_command import command_deploy
from armada_command import command_develop
from armada_command import command_diagnose
from armada_command import command_dockyard
from armada_command import command_info
from armada_command import command_list
from armada_command import command_name
from armada_command import command_poker
from armada_command import command_push
from armada_command import command_recover
from armada_command import command_restart
from armada_command import command_run
from armada_command import command_shutdown
from armada_command import command_ssh
from armada_command import command_stop
from armada_command import command_version
from armada_command._version import __version__
from armada_command.armada_logging import log_command
from armada_command.armada_utils import set_verbose, is_verbose
from armada_command.scripts.update import version_check


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')

    subparsers = parser.add_subparsers(dest='subparser_command')

    parser_name_help = 'get/set name for this ship'
    parser_name = subparsers.add_parser('name', help=parser_name_help, description=parser_name_help)
    command_name.add_arguments(parser_name)
    parser_name.set_defaults(func=command_name.command_name)

    parser_join_help = 'join another armada'
    parser_join = subparsers.add_parser('join', help=parser_join_help, description=parser_join_help)
    parser_join.add_argument('address', help='IP/hostname of any ship in armada we want to join')
    parser_join.set_defaults(func=command_join)

    parser_promote_help = 'promote ship to commander role'
    parser_promote = subparsers.add_parser('promote', help=parser_promote_help, description=parser_promote_help)
    parser_promote.set_defaults(func=command_promote)

    parser_shutdown_help = 'gently remove ship from armada and prepare for service shutdown'
    parser_shutdown = subparsers.add_parser('shutdown', help=parser_shutdown_help, description=parser_shutdown_help)
    command_shutdown.add_arguments(parser_shutdown)
    parser_shutdown.set_defaults(func=command_shutdown.command_shutdown)

    parser_dockyard_help = 'manage dockyard aliases'
    parser_dockyard = subparsers.add_parser('dockyard', help=parser_dockyard_help, description=parser_dockyard_help)
    command_dockyard.add_arguments(parser_dockyard)
    parser_dockyard.set_defaults(func=command_dockyard.command_dockyard)

    parser_list_help = 'show list of running microservices'
    parser_list = subparsers.add_parser('list', help=parser_list_help, description=parser_list_help)
    command_list.add_arguments(parser_list)
    parser_list.set_defaults(func=command_list.command_list)

    parser_info_help = 'show list of ships within current armada'
    parser_info = subparsers.add_parser('info', help=parser_info_help, description=parser_info_help)
    parser_info.set_defaults(func=command_info.command_info)

    parser_run_help = 'run container with microservice'
    parser_run = subparsers.add_parser('run', help=parser_run_help, description=parser_run_help)
    command_run.add_arguments(parser_run)
    parser_run.set_defaults(func=command_run.command_run)

    parser_deploy_help = 'EXPERIMENTAL! deploy (restart and/or run) microservices'
    parser_deploy = subparsers.add_parser('deploy', help=parser_deploy_help, description=parser_deploy_help)
    command_deploy.add_arguments(parser_deploy)
    parser_deploy.set_defaults(func=command_deploy.command_deploy)

    parser_stop_help = 'stop container with microservice'
    parser_stop = subparsers.add_parser('stop', help=parser_stop_help, description=parser_stop_help)
    command_stop.add_arguments(parser_stop)
    parser_stop.set_defaults(func=command_stop.command_stop)

    parser_restart_help = 'restart container with microservice'
    parser_restart = subparsers.add_parser('restart', help=parser_restart_help, description=parser_restart_help)
    command_restart.add_arguments(parser_restart)
    parser_restart.set_defaults(func=command_restart.command_restart)

    parser_recover_help = 'run containers from JSON file with saved containers\' parameters'
    parser_recover = subparsers.add_parser('recover', help=parser_recover_help, description=parser_recover_help)
    command_recover.add_arguments(parser_recover)
    parser_recover.set_defaults(func=command_recover.command_recover)

    parser_ssh_help = 'ssh into container with microservice'
    parser_ssh = subparsers.add_parser('ssh', help=parser_ssh_help, description=parser_ssh_help)
    command_ssh.add_arguments(parser_ssh)
    parser_ssh.set_defaults(func=command_ssh.command_ssh)

    parser_build_help = 'build container with microservice'
    parser_build = subparsers.add_parser('build', help=parser_build_help, description=parser_build_help)
    command_build.add_arguments(parser_build)
    parser_build.set_defaults(func=command_build.command_build)

    parser_push_help = 'push container with microservice to dockyard'
    parser_push = subparsers.add_parser('push', help=parser_push_help, description=parser_push_help)
    command_push.add_arguments(parser_push)
    parser_push.set_defaults(func=command_push.command_push)

    parser_create_help = 'create skeleton for new microservice'
    parser_create = subparsers.add_parser('create', help=parser_create_help, description=parser_create_help)
    command_create.add_arguments(parser_create)
    parser_create.set_defaults(func=command_create.command_create)

    parser_version_help = 'display armada version'
    parser_version = subparsers.add_parser('version', help=parser_version_help, description=parser_version_help)
    parser_version.set_defaults(func=command_version.command_version)

    parser_diagnose_help = 'run diagnostic check on a container'
    parser_diagnose = subparsers.add_parser('diagnose', help=parser_diagnose_help, description=parser_diagnose_help)
    command_diagnose.add_arguments(parser_diagnose)
    parser_diagnose.set_defaults(func=command_diagnose.command_diagnose)

    parser_develop_help = 'set up development environment for microservice'
    parser_develop = subparsers.add_parser('develop', help=parser_develop_help, description=parser_develop_help)
    command_develop.add_arguments(parser_develop)
    parser_develop.set_defaults(func=command_develop.command_develop)

    parser_poker = subparsers.add_parser('poker')
    parser_poker.set_defaults(func=command_poker.command_poker)

    for subparser in subparsers.choices.values():
        subparser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')

    return parser


# ===================================================================================================


def command_join(args):
    result = armada_api.post('join', {'host': args.address})
    armada_api.print_result_from_armada_api(result)


def command_promote(args):
    result = armada_api.post('promote')
    armada_api.print_result_from_armada_api(result)


# ===================================================================================================

def _load_armada_develop_vars():
    path = command_develop.get_armada_develop_env_file_path()
    if not os.path.isfile(path):
        return
    with open(path) as f:
        envs = json.load(f)
        os.environ.update(envs)


@version_check
def main():
    # https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
    # We don't want Insecure Platform Warning to pop up everytime HTTPS request is sent.
    urllib3.disable_warnings()

    log_command()

    parser = _get_parser()
    args = parser.parse_args()
    try:
        if args.verbose:
            set_verbose()
    except AttributeError:
        pass

    try:
        _load_armada_develop_vars()
    except Exception:
        print('Warning: Could not load armada develop vars.')
        if is_verbose():
            traceback.print_exc()

    try:
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_usage()
    except Exception as e:
        print('Command failed: {exception_class} - {exception}'.format(
            exception_class=type(e).__name__,
            exception=str(e)))
        if is_verbose():
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
