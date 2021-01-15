import datetime

from armada_command.armada_api import get_json
from armada_command.armada_utils import print_table


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
    parser.add_argument('--microservice-version', action='store_true',
                        help='Show column with microservice package version.')


def epoch_to_iso(unix_timestamp):
    if unix_timestamp is None:
        return 'n/a'
    return datetime.datetime.utcfromtimestamp(
        int(unix_timestamp)).strftime('%Y-%m-%d %H:%M')


def command_list(args):
    service_list = get_json('list', vars(args))

    if args.quiet:
        for container_id in {service['container_id'] for service in service_list}:
            print(container_id)
        return

    output_header = ['Name', 'Address', 'ID', 'Status', 'Env', 'AppID']
    if args.uptime:
        output_header.append("Created (UTC)")
    if args.microservice_version:
        output_header.append("Microservice Version")
    output_rows = [output_header]

    for service in service_list:
        service_tags = service['tags']

        output_row = [service['name'], service['address'], service['container_id'], service['status'],
                      service_tags.get('env') or '-', service_tags.get('app_id') or '-']
        if args.uptime:
            creation_time = epoch_to_iso(service['start_timestamp'])
            output_row.append(creation_time)
        if args.microservice_version:
            microservice_version = service.get('microservice_version', '?')
            output_row.append(microservice_version)
        output_rows.append(output_row)

    print_table(output_rows)
