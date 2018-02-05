import fnmatch
import random
from distutils.util import strtobool

import six

from armada_backend import api_base
from armada_backend.models.ships import get_ship_name
from armada_backend.utils import get_logger
from armada_command.consul import kv
from armada_command.consul.consul import consul_query


class List(api_base.ApiCommand):
    def on_get(self, req, resp):
        try:
            microservice_name = req.get_param('microservice_name')
            microservice_env = req.get_param('env')
            microservice_app_id = req.get_param('app_id')
            local_param = req.get_param('local', default=False)
            local = bool(local_param and strtobool(str(local_param)))

            services_list = get_list(microservice_name, microservice_env, microservice_app_id, local)

            return self.status_ok(resp, {'result': services_list})
        except Exception as e:
            return self.status_exception(resp, "Cannot get the list of services.", e)


def get_list(microservice_name=None, microservice_env=None, microservice_app_id=None, local=False):
    filters = {
        'filter_microservice_name': microservice_name,
        'filter_env': microservice_env,
        'filter_app_id': microservice_app_id,
        'filter_local': local,
    }

    services_list = _get_services_list(**filters)
    running_services = _get_running_services(**filters)
    for container_id, service_dict in six.iteritems(running_services):
        if container_id in services_list:
            services_list[container_id].update(service_dict)
        else:
            services_list[container_id] = service_dict
    services_list = _choose_active_instances(services_list, filters['filter_local'])

    return sorted(six.itervalues(services_list), key=_extended_sort_info)


def _extended_sort_info(service):
    name_subservice = service['name'].split(':')
    ip_port = service['address'].split(':')

    if len(name_subservice) == 1:
        name_subservice.append('')

    clean_name, subservice_name = name_subservice

    ip = ip_port[0]

    env = service['tags'].get('env', '')
    app_id = service['tags'].get('app_id', '')

    return (clean_name, env, app_id, ip, service['microservice_id'])


def __create_dict_from_tags(tags):
    if not tags:
        return {}
    return dict((tag.split(':', 1) + [None])[:2] for tag in tags)


def _get_services_list(filter_microservice_name, filter_env, filter_app_id, filter_local):
    consul_key = 'services'
    if filter_local:
        consul_key = '{}/{}'.format(consul_key, get_ship_name())

    services_by_ship = kv.kv_get_recurse(consul_key)

    if not services_by_ship:
        return {}

    return _parse_single_ship(services_by_ship, filter_microservice_name, filter_env, filter_app_id)


def _get_running_services(filter_microservice_name, filter_env, filter_app_id, filter_local):
    if filter_local:
        local_microservices_ids = set(consul_query('agent/services'))
    if filter_microservice_name:
        names = list(consul_query('catalog/services'))
        microservices_names = fnmatch.filter(names, filter_microservice_name)
    else:
        microservices_names = list(consul_query('catalog/services'))
    start_timestamps = kv.kv_get_recurse('start_timestamp/') or {}
    single_active_instances = kv.kv_get_recurse('single_active_instance/')
    if single_active_instances:
        single_active_instances_list = list(single_active_instances)
    else:
        single_active_instances_list = []
    services_list_from_catalog = {}
    for microservice_name in microservices_names:
        if microservice_name == 'consul':
            continue

        query = 'health/service/{microservice_name}'.format(**locals())
        instances = consul_query(query)
        for instance in instances:
            microservice_checks_statuses = set(check['Status'] for check in (instance['Checks'] or []))
            microservice_computed_status = '-'
            for possible_status in ['passing', 'warning', 'critical']:
                if possible_status in microservice_checks_statuses:
                    microservice_computed_status = possible_status

            microservice_ip = instance['Node']['Address']
            microservice_port = str(instance['Service']['Port'])
            microservice_id = instance['Service']['ID']
            container_id = microservice_id.split(':')[0]
            microservice_tags = instance['Service']['Tags'] or []
            microservice_tags_dict = __create_dict_from_tags(microservice_tags)

            matches_env = (filter_env is None) or (filter_env == microservice_tags_dict.get('env'))
            matches_app_id = (filter_app_id is None) or (filter_app_id == microservice_tags_dict.get('app_id'))

            if (matches_env and matches_app_id and
                    (not filter_local or microservice_id in local_microservices_ids)):
                microservice_address = microservice_ip + ':' + microservice_port
                microservice_start_timestamp = start_timestamps.get(container_id, None)
                single_active_instance = microservice_id in single_active_instances_list

                microservice_dict = {
                    'name': microservice_name,
                    'address': microservice_address,
                    'microservice_id': microservice_id,
                    'container_id': container_id,
                    'status': microservice_computed_status,
                    'tags': microservice_tags_dict,
                    'start_timestamp': microservice_start_timestamp,
                    'single_active_instance': single_active_instance,
                }
                services_list_from_catalog[microservice_id] = microservice_dict
    return services_list_from_catalog


def _parse_single_ship(services_dict, filter_microservice_name, filter_env, filter_app_id):
    try:
        services_list = list(services_dict)
    except AttributeError:
        services_list = None

    result = {}
    if not services_list:
        return result

    if filter_microservice_name:
        services_list = fnmatch.filter(services_list, 'services/*/{}/*'.format(filter_microservice_name))

    for service in services_list:
        service_dict = services_dict[service]
        microservice_name = service_dict['ServiceName']
        microservice_status = service_dict['Status']
        microservice_id = service_dict['ServiceID']
        container_id = service_dict['container_id']
        microservice_start_timestamp = service_dict['start_timestamp']
        single_active_instance = service_dict.get('single_active_instance', False)
        microservice_version = service_dict.get('microservice_version')
        not_available = 'n/a'

        microservice_tags_dict = {}
        try:
            if service_dict['params']['microservice_env']:
                microservice_tags_dict['env'] = service_dict['params']['microservice_env']
            if service_dict['params']['microservice_app_id']:
                microservice_tags_dict['app_id'] = service_dict['params']['microservice_app_id']
        except KeyError as e:
            get_logger().warning(repr(e))

        matches_env = (filter_env is None) or (filter_env == microservice_tags_dict.get('env'))
        matches_app_id = (filter_app_id is None) or (filter_app_id == microservice_tags_dict.get('app_id'))

        if matches_env and matches_app_id:
            microservice_dict = {
                'name': microservice_name,
                'status': microservice_status,
                'address': not_available,
                'microservice_id': microservice_id,
                'container_id': container_id,
                'tags': microservice_tags_dict,
                'start_timestamp': microservice_start_timestamp,
                'single_active_instance': single_active_instance,
            }
            if microservice_version:
                microservice_dict['microservice_version'] = microservice_version
            result[microservice_id] = microservice_dict

    return result


def _choose_active_instances(services_dicts, filter_local):
    result = services_dicts
    running_services_with_single_active_instances = {}
    for microservice_id, service_dict in six.iteritems(services_dicts):
        if service_dict.get('single_active_instance') and service_dict['status'] in ('passing', 'warning'):
            key = 'chosen_active_instance/{},env={},app_id={}'.format(service_dict['name'],
                                                                      service_dict['tags'].get('env') or '',
                                                                      service_dict['tags'].get('app_id') or '')
            if key not in running_services_with_single_active_instances:
                running_services_with_single_active_instances[key] = set()
            running_services_with_single_active_instances[key].add(microservice_id)

    for key, running_microservice_ids in six.iteritems(running_services_with_single_active_instances):
        currently_picked_instance = kv.kv_get(key)
        if not filter_local and currently_picked_instance not in running_microservice_ids:
            currently_picked_instance = random.choice(list(running_microservice_ids))
            kv.kv_set(key, currently_picked_instance)
        for microservice_id in running_microservice_ids:
            if microservice_id != currently_picked_instance:
                result[microservice_id]['status'] = 'standby'
    return result
