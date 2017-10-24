from __future__ import print_function

import argparse
import os
import sys
import logging

from armada import hermes

import local_magellan


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
    if env:
        microservice['env'] = env
    elif 'MICROSERVICE_ENV' in os.environ:
        microservice['env'] = os.environ.get('MICROSERVICE_ENV')
    if app_id:
        microservice['app_id'] = app_id
    elif 'MICROSERVICE_APP_ID' in os.environ:
        microservice['app_id'] = os.environ.get('MICROSERVICE_APP_ID')
    magellan_config = {port: microservice}
    print(magellan_config)
    local_magellan.save_magellan_config(magellan_config)


def main():
    args = parse_args()

    file_name = args.config

    if not file_name:
        if not args.microservice_name or not args.port:
            raise RuntimeError('microservice_name and port are required')
        else:
            configure_single_requirement(args.microservice_name, args.port, args.env, args.app_id)
    else:
        create_magellan_config_from_file(file_name)


if __name__ == '__main__':
    main()
