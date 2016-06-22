import argparse

import armada_api


def parse_args():
    parser = argparse.ArgumentParser(description="Display armada version.")
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('-vv', '--verbose', action='store_true', help='Increase output verbosity.')


def command_version(args):
    version = armada_api.get('version')
    print(version)
