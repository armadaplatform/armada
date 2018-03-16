from subprocess import check_call

from armada_backend.utils import get_logger
from armada_command.consul import kv
from armada_command.consul.consul import consul_query


def get_ship_ip():
    """
    It get ship advertise IP address.
    It can be different than external IP, when external IP changes after ship first start.
    """

    agent_self_dict = consul_query('agent/self')
    return agent_self_dict['Config']['AdvertiseAddr']


def get_ship_name(ship_ip=None):
    if ship_ip is None:
        ship_ip = get_ship_ip()
    ship_name = kv.kv_get('ships/{}/name'.format(ship_ip)) or ship_ip
    return ship_name


def get_ship_ip_and_name():
    ship_ip = get_ship_ip()
    ship_name = get_ship_name(ship_ip)
    return ship_ip, ship_name


def set_ship_name(new_name):
    from armada_backend.models.services import get_services_by_ship, create_consul_services_key
    ship_ip = get_ship_ip()
    old_name = get_ship_name(ship_ip)
    saved_containers = get_services_by_ship(old_name)
    if saved_containers:
        for container in saved_containers:
            new_key = create_consul_services_key(ship=new_name, service_name=container.split('/')[-2],
                                                 container_id=container.split('/')[-1])
            container_dict = kv.kv_get(container)
            kv.kv_set(new_key, container_dict)
            kv.kv_remove(container)
    kv.kv_set('ships/{}/name'.format(ship_ip), new_name)
    kv.kv_set('ships/{}/ip'.format(new_name), ship_ip)
    check_call('sed -i \'s|ships/{}/|ships/{}/|\' /etc/consul.config'.format(old_name, new_name), shell=True)
    try:
        check_call(['/usr/local/bin/consul', 'reload'])
    except Exception as e:
        get_logger().exception(e)


def get_other_ship_ips():
    try:
        catalog_nodes_dict = consul_query('catalog/nodes')
        ship_ips = list(consul_node['Address'] for consul_node in catalog_nodes_dict)

        my_ship_ip = get_ship_ip()
        if my_ship_ip in ship_ips:
            ship_ips.remove(my_ship_ip)
        return ship_ips
    except Exception as e:
        get_logger().exception(e)
        return []
