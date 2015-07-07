from __future__ import print_function
import argparse
import os
import sys

import local_magellan


def print_err(*objs):
    print(*objs, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(description='Make given microservice available at local HAProxy.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('port',
                        type=int,
                        help='Bind port. Given microservice will be available at localhost:port.')
    parser.add_argument('microservice_name',
                        help='Name of the microservice.')
    parser.add_argument('--env',
                        help='Environment of the microservice. Default: environment variable $MICROSERVICE_ENV.')
    parser.add_argument('--app_id',
                        help='Application ID of the microservice. Default: environment variable $MICROSERVICE_APP_ID.')


def create_magellan_config(port, microservice_name, env, app_id):
    microservice = {'microservice_name': microservice_name}
    if env:
        microservice['env'] = env
    if app_id:
        microservice['app_id'] = app_id
    magellan_config = {
        port: microservice
    }
    local_magellan.save_magellan_config(magellan_config)


def main():
    args = parse_args()
    env = args.env
    if env is None:
        env = os.environ.get('MICROSERVICE_ENV')
    app_id = args.app_id
    if app_id is None:
        app_id = os.environ.get('MICROSERVICE_APP_ID')
    create_magellan_config(args.port, args.microservice_name, env, app_id)


if __name__ == '__main__':
    main()
