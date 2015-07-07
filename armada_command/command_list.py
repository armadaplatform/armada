from __future__ import print_function
import argparse
from armada_command.consul.consul import consul_query
from armada_command.consul import kv
import datetime


def parse_args():
    parser = argparse.ArgumentParser(description='Show list of running microservices.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    parser.add_argument('service_name',
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


def print_table(rows):
    widths = [max(len(str(val)) for val in col) for col in zip(*rows)]
    for row in rows:
        print('  '.join((str(val).ljust(width) for val, width in zip(row, widths))))


def epoch_to_iso(unix_timestamp):
    return datetime.datetime.utcfromtimestamp(
        int(unix_timestamp)).strftime('%Y-%m-%d %H:%M')


def command_list(args):
    if args.service_name:
        service_names = [args.service_name]
    else:
        service_names = list(consul_query('catalog/services').keys())

    if args.local:
        local_ids = set(consul_query('agent/services').keys())

    if not args.quiet:
        output_header = ('Name', 'Address', 'ID', 'Status', 'Tags')
        if args.uptime:
            output_header += ("Created (UTC)",)
        output_rows = [output_header]

    for service_name in service_names:
        if service_name == 'consul':
            continue

        query = 'health/service/{service_name}'.format(**locals())
        instances = consul_query(query)
        for instance in instances:
            service_checks_statuses = set(check['Status'] for check in (instance['Checks'] or []))
            service_computed_status = '-'
            for possible_status in ['passing', 'warning', 'critical']:
                if possible_status in service_checks_statuses:
                    service_computed_status = possible_status

            service_ip = instance['Node']['Address']
            service_port = str(instance['Service']['Port'])
            service_id = instance['Service']['ID']
            container_id = service_id.split(':')[0]
            service_tags = instance['Service']['Tags'] or []
            service_tags_pretty = [str(x) for x in sorted(service_tags)] if service_tags else '-'
            service_tags_set = set(service_tags)

            matches_env = (args.env is None) or ('env:' + args.env in service_tags_set)
            matches_app_id = (args.app_id is None) or ('app_id:' + args.app_id in service_tags_set)
            if matches_env and matches_app_id and (not args.local or service_id in local_ids):
                service_address = service_ip + ':' + service_port
                if args.quiet:
                    print(str(container_id))
                else:
                    output_row = (service_name, service_address, container_id, service_computed_status, service_tags_pretty)
                    if args.uptime:
                        try:
                            start_timestamp = kv.get("start_timestamp/" + container_id)
                            creation_time = epoch_to_iso(start_timestamp)
                        except:
                            creation_time = "-"
                        output_row += (creation_time,)

                    output_rows.append(output_row)

    if not args.quiet:
        print_table([output_rows[0]] + sorted(output_rows[1:]))
