from __future__ import print_function

import datetime

from armada_command.armada_api import get_json
from armada_utils import print_table
from operator import itemgetter


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

def sort_list(service_list):
    unsorted_list = list()
    for i, service in enumerate(service_list):
        name_subname = service[0].split(":")
        if len(name_subname) == 1:
            name_subname.append('')
        name, subname = name_subname

        ip_port = service[1].split(":")
        ip = ip_port[0]

        unsorted_list.append(list(service))
        unsorted_list[i].append(name)
        unsorted_list[i].append(subname)
        unsorted_list[i].append(ip)

    sorted_list = sorted(unsorted_list, key=itemgetter(6,4,5,8,2,7))

    return sorted_list

def command_list(args):

    service_list = get_json('list', vars(args))

    output_rows = []

    if not args.quiet:
        output_header = ('Name', 'Address', 'ID', 'Status', 'Env', 'AppID')
        if args.uptime:
            output_header += ("Created (UTC)",)
        output_rows = [output_header]

    if args.quiet:
        for container_id in {service['container_id'] for service in service_list}:
            print(container_id)
    else:
        for service in service_list:
            service_tags = service['tags']

            output_row = (service['name'], service['address'], service['container_id'], service['status'],
                          service_tags.get('env') or '-', service_tags.get('app_id') or '-')
            if args.uptime:
                creation_time = epoch_to_iso(service['start_timestamp'])
                output_row += (creation_time,)
            output_rows.append(output_row)

        print_table([output_rows[0]] + sort_list(output_rows[1:]))
