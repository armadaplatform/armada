import argparse
import logging
import os
import sys

from microservice.local_magellan import local_magellan

from armada import hermes


def print_err(*objs):
    print(*objs, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(description='Make given microservice available at local HAProxy.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('port', nargs='?',
                        type=int,
                        help='Bind port. Given microservice will be available at localhost:port.')
    parser.add_argument('microservice_name', nargs='?',
                        help='Name of the microservice.')
    parser.add_argument('--env',
                        help='Environment of the microservice. Default: environment variable $MICROSERVICE_ENV.')
    parser.add_argument('--app_id',
                        help='Application ID of the microservice. Default: environment variable $MICROSERVICE_APP_ID.')
    parser.add_argument('-c', '--config',
                        help='Name of file with configuration. It should be located in config directory.')


def create_magellan_config_from_file(file_name):
    config = hermes.get_config(file_name)

    if config:
        for microservice_name, configurations in config.items():
            if isinstance(configurations, list):
                for configuration in configurations:
                    configure_single_requirement(microservice_name, **configuration)

            elif isinstance(configurations, dict):
                configure_single_requirement(microservice_name, **configurations)
    else:
        logging.warning('Empty dependency file: {}'.format(file_name))


def configure_single_requirement(microservice_name, port, env=None, app_id=None):
    microservice = {'microservice_name': microservice_name}

    if env is None:
        env = os.environ.get('MICROSERVICE_ENV')
    if env:
        microservice['env'] = env

    if app_id is None:
        app_id = os.environ.get('MICROSERVICE_APP_ID')
    if app_id:
        microservice['app_id'] = app_id

    magellan_config = {port: microservice}
    local_magellan.save_magellan_config(magellan_config)


def main(args):
    file_name = args.config

    if not file_name:
        if not args.port or not args.microservice_name:
            raise RuntimeError('port and microservice_name are required')
        else:
            configure_single_requirement(args.microservice_name, args.port, args.env, args.app_id)
    else:
        create_magellan_config_from_file(file_name)


if __name__ == '__main__':
    print('WARNING: Calling this script directly has been deprecated. Try `microservice require` instead.',
          file=sys.stderr)
    args = parse_args()
    main(args)
