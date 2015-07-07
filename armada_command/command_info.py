from __future__ import print_function
import argparse
import sys
from armada_command.consul.consul import consul_query
import requests


def parse_args():
    parser = argparse.ArgumentParser(description='Show list of ships within current armada.')
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    pass


def print_table(rows):
    widths = [max(len(str(val)) for val in col) for col in zip(*rows)]
    for row in rows:
        print('  '.join((str(val).ljust(width) for val, width in zip(row, widths))))


def get_ship_role(ship_ip):
    status_leader = consul_query('status/leader')

    ship_role = 'ship'
    ship_info = consul_query('agent/self', consul_address='{ship_ip}:8500'.format(**locals()))
    if ship_info['Config']['Server']:
        ship_role = 'commander'
        if status_leader.startswith(ship_ip + ':'):
            ship_role = 'leader'

    return ship_role


def get_armada_address(ship_name):
    catalog_service_armada = consul_query('catalog/service/armada')

    for service_armada in catalog_service_armada:
        if service_armada['Node'] == ship_name:
            return service_armada['Address'] + ':' + str(service_armada['ServicePort'])
    return None


def get_armada_status(ship_name):
    health_service_armada = consul_query('health/service/armada')

    service_armada_status = '-'
    for health_armada in health_service_armada:
        if health_armada['Node']['Node'] == ship_name:
            service_checks_statuses = set(check['Status'] for check in (health_armada['Checks'] or []))
            for possible_status in ['passing', 'warning', 'critical']:
                if possible_status in service_checks_statuses:
                    service_armada_status = possible_status
            return service_armada_status

    return service_armada_status


def get_armada_version(address):
    url = "http://{address}/version".format(address=address)
    try:
        result = requests.get(url)
        version = result.text
    except Exception:
        version = "error"

    return version


def command_info(args):
    catalog_nodes_dict = consul_query('catalog/nodes')

    output_header = ['Ship name', 'Ship role', 'API address', 'API status', 'Version']
    output_rows = [output_header]
    ship_role_counts = { 'ship': 0, 'commander': 0, 'leader' : 0, '?' : 0 }
    for consul_node in catalog_nodes_dict:
        ship_name = consul_node['Node']
        ship_ip = consul_node['Address']

        service_armada_address = get_armada_address(ship_name) or ship_ip
        service_armada_status = get_armada_status(ship_name)
        service_armada_version = get_armada_version(service_armada_address)
        try:
            ship_role = get_ship_role(ship_ip)
        except:
            ship_role = '?'

        if service_armada_status == 'passing':
            ship_role_counts[ship_role] += 1

        if ship_name.startswith('ship-'):
            ship_name = ship_name[5:]

        output_rows.append([ship_name, ship_role, service_armada_address, service_armada_status, service_armada_version])

    print_table(output_rows)

    if ship_role_counts['leader'] == 0:
        print('\nERROR: There is no active leader. Armada is not working!', file = sys.stderr)
    elif ship_role_counts['commander'] == 0:
        print('\nWARNING: We cannot survive leader leaving/failure.', file = sys.stderr)
        print('Such configuration should only be used in development environments.', file = sys.stderr)
    elif ship_role_counts['commander'] == 1:
        print('\nWARNING: We can survive leaving of commander but commander failure or leader leave/failure will be fatal.', file = sys.stderr)
        print('Such configuration should only be used in development environments.', file = sys.stderr)
    else:
        failure_tolerance = ship_role_counts['commander'] / 2
        print('\nWe can survive failure of ' + str(failure_tolerance) + str(' commander' if failure_tolerance == 1 else ' commanders') + ' (including leader).', file = sys.stderr)
