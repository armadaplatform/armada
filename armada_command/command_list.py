from __future__ import print_function

import datetime

from armada_command.armada_api import get_json
from armada_utils import print_table


def add_arguments(parser):
    parser.add_argument('microservice_name',
                        nargs='?',
                        help='Name of the microservice to be discovered.\n'
                             'If not provided, it will display all running microservices.')
    parser.add_argument('-e', '--env',
                        help='Filter services by their environment (consul tag "env").')
    parser.add_argument('-a', '--app_id',
                        help='Filter services by their app_id (consul tag "app_id").')
    parser.add_argument('-l', '--local', action='store_true', help='Show only services that are running on local ship.')
    parser.add_argument('-u', '--uptime', action='store_true', help="Displays startup time")
    parser.add_argument('-q', '--quiet', action='store_true', help='Show only container ids.')


def epoch_to_iso(unix_timestamp):
    if unix_timestamp is None:
        return 'n/a'
    return datetime.datetime.utcfromtimestamp(
        int(unix_timestamp)).strftime('%Y-%m-%d %H:%M')


def command_list(args):
    service_list = get_json('list', vars(args))

    output_rows = None

    if not args.quiet:
        output_header = ('Name', 'Address', 'ID', 'Status', 'Tags')
        if args.uptime:
            output_header += ("Created (UTC)",)
        output_rows = [output_header]

    for service in service_list:
        if args.quiet:
            print(str(service['container_id']))
        else:
            service_tags_pretty = [str(x) + ':' + str(service['tags'][x])
                                   for x in sorted(service['tags'])] if service['tags'] else '-'
            output_row = (service['name'], service['address'], service['container_id'], service['status'],
                          service_tags_pretty)
            if args.uptime:
                creation_time = epoch_to_iso(service['start_timestamp'])
                output_row += (creation_time,)
            output_rows.append(output_row)

    if not args.quiet:
        print_table([output_rows[0]] + sorted(output_rows[1:]))
