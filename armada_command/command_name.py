import argparse

import armada_api


def parse_args():
    parser = argparse.ArgumentParser(description="Get/Set name for this ship.")
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('name', help='New name for the ship', nargs='?', default='')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity.')


def command_name(args):
    if args.name:
        result = armada_api.post('name', {'name': args.name})
        armada_api.print_result_from_armada_api(result)
    else:
        result = armada_api.get('name')
        print(result)
