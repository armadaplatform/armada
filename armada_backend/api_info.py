import requests

from armada_backend import api_base
from armada_backend.api_list import get_list
from armada_backend.models.ships import get_ship_ip, get_ship_name
from armada_backend.utils import get_logger
from armada_command.consul.consul import consul_query


def get_ship_role(ship_ip):
    status_leader = consul_query('status/leader')

    ship_role = 'ship'
    ship_info = consul_query('agent/self', consul_address='{ship_ip}:8500'.format(**locals()))
    if ship_info['Config']['Server']:
        ship_role = 'commander'
        if status_leader.startswith(ship_ip + ':'):
            ship_role = 'leader'

    return ship_role


def get_armada_version(address):
    url = "http://{address}/version".format(address=address)
    version = "error"
    try:
        result = requests.get(url, timeout=0.5)
        result.raise_for_status()
        version = result.text.split()[0]
    except Exception as e:
        get_logger().exception(e)

    return version


def _get_running_armada_services():
    return get_list('armada')


def _create_ip_to_service(services):
    return {service['address'].split(':')[0]: service for service in services}


class Info(api_base.ApiCommand):
    def on_get(self, req, resp):
        try:
            catalog_nodes_dict = consul_query('catalog/nodes')

            result = []
            running_armada_services = _get_running_armada_services()
            ship_ip_to_armada = _create_ip_to_service(running_armada_services)
            current_ship_ip = get_ship_ip()
            for consul_node in catalog_nodes_dict:
                ship_ip = consul_node['Address']
                ship_name = get_ship_name(ship_ip)
                armada_service = ship_ip_to_armada.get(ship_ip, {})

                service_armada_address = armada_service.get('address', ship_ip)
                service_armada_status = armada_service.get('status', '?')
                service_armada_version = get_armada_version(service_armada_address)
                try:
                    ship_role = get_ship_role(ship_ip)
                except Exception as e:
                    get_logger().exception(e)
                    ship_role = '?'

                is_current = (ship_ip == current_ship_ip)

                armada_instance = {
                    'name': ship_name,
                    'role': ship_role,
                    'address': service_armada_address,
                    'status': service_armada_status,
                    'version': service_armada_version,
                    'microservice_id': armada_service.get('microservice_id'),
                    'is_current': is_current
                }
                result.append(armada_instance)
        except Exception as e:
            return self.status_exception(resp, 'Could not get armada info.', e)
        return self.status_ok(resp, {'result': result})
