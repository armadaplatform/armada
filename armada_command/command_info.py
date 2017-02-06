from __future__ import print_function

import sys
from collections import Counter

import armada_api
from armada_utils import print_table


def command_info(args):
    info = armada_api.get_json('info')

    output_header = ['Current', 'Ship name', 'Ship role', 'API address', 'API status', 'Version']
    output_rows = [output_header]

    ship_role_counts = Counter()
    for ship in info:
        current_string = '->'.rjust(len(output_header[0])) if ship['is_current'] else ''
        if ship['status'] == 'passing':
            ship_role_counts[ship['role']] += 1
        output_rows.append([current_string, ship['name'], ship['role'], ship['address'], ship['status'],
                            ship['version']])

    print_table(output_rows)

    if ship_role_counts['leader'] == 0:
        print('\nERROR: There is no active leader. Armada is not working!', file=sys.stderr)
    elif ship_role_counts['commander'] == 0:
        print('\nWARNING: We cannot survive leader leaving/failure.', file=sys.stderr)
        print('Such configuration should only be used in development environments.', file=sys.stderr)
    elif ship_role_counts['commander'] == 1:
        print('\nWARNING: We can survive leaving of commander but commander failure or leader leave/failure will be '
              'fatal.', file=sys.stderr)
        print('Such configuration should only be used in development environments.', file=sys.stderr)
    else:
        failure_tolerance = ship_role_counts['commander'] / 2
        print('\nWe can survive failure of {0} {1} (including leader).'.format(
            failure_tolerance, 'commander' if failure_tolerance == 1 else 'commanders'),
            file=sys.stderr)
