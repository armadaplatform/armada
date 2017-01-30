from __future__ import print_function

import argparse
import sys
import traceback

from requests.packages import urllib3

import armada_api
import command_build
import command_create
import command_diagnose
import command_dockyard
import command_info
import command_list
import command_name
import command_push
import command_recover
import command_restart
import command_run
import command_ssh
import command_stop
import command_version
from _version import __version__
from armada_command import command_shutdown
from armada_command.scripts.update import version_check
from armada_logging import log_command
from armada_utils import set_verbose, is_verbose


def parse_args():
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

    for subparser in subparsers.choices.values():
        subparser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')

    args = parser.parse_args()
    return args


# ===================================================================================================


def command_join(args):
    result = armada_api.post('join', {'host': args.address})
    armada_api.print_result_from_armada_api(result)


def command_promote(args):
    result = armada_api.post('promote')
    armada_api.print_result_from_armada_api(result)


# ===================================================================================================

@version_check
def main():
    # https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
    # We don't want Insecure Platform Warning to pop up everytime HTTPS request is sent.
    urllib3.disable_warnings()

    log_command()

    args = parse_args()
    try:
        if args.verbose:
            set_verbose()
    except AttributeError:
        pass
    try:
        args.func(args)
    except Exception as e:
        print('Command failed: {exception_class} - {exception}'.format(
            exception_class=type(e).__name__,
            exception=str(e)))
        if is_verbose():
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
