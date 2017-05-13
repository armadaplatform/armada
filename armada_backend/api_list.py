import fnmatch
import random
from distutils.util import strtobool

import web

from armada_backend import api_base
from armada_backend.utils import get_ship_name, get_logger
from armada_command.consul import kv
from armada_command.consul.consul import consul_query


class List(api_base.ApiCommand):
    @staticmethod
    def __create_dict_from_tags(tags):
        if not tags:
            return {}
        return dict((tag.split(':', 1) + [None])[:2] for tag in tags)

    def GET(self):
        try:
            get_args = web.input(local=False, microservice_name=None, env=None, app_id=None)
            filter_local = bool(get_args.local and strtobool(str(get_args.local)))
            filter_microservice_name = get_args.microservice_name
            filter_env = get_args.env
            filter_app_id = get_args.app_id

            services_list = _get_services_list(filter_microservice_name, filter_env, filter_app_id, filter_local)

            if filter_local:
                local_microservices_ids = set(consul_query('agent/services').keys())

            if filter_microservice_name:
                names = list(consul_query('catalog/services').keys())
                microservices_names = fnmatch.filter(names, filter_microservice_name)
            else:
                microservices_names = list(consul_query('catalog/services').keys())

            start_timestamps = kv.kv_get_recurse('start_timestamp/') or {}

            single_active_instances = kv.kv_get_recurse('single_active_instance/')
            if single_active_instances:
                single_active_instances_list = single_active_instances.keys()
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
                    microservice_tags_dict = self.__create_dict_from_tags(microservice_tags)

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

            result = services_list
            result.update(services_list_from_catalog)
            result = _choose_active_instances(result)
            return self.status_ok({'result': result.values()})
        except Exception as e:
            return self.status_exception("Cannot get the list of services.", e)


def _get_services_list(filter_microservice_name, filter_env, filter_app_id, filter_local):
    ships_key = 'ships'
    if filter_local:
        ships_key = "{}/{}".format(ships_key, get_ship_name())

    services_dict = kv.kv_get_recurse(ships_key)

    if not services_dict:
        return {}

    services_list = services_dict.keys()

    result = {}
    if not services_list:
        return result

    if filter_microservice_name:
        services_list = fnmatch.filter(services_list, '*/service/{}/*'.format(filter_microservice_name))

    for service in services_list:
        service_dict = services_dict[service]
        microservice_name = service_dict['ServiceName']
        microservice_status = service_dict['Status']
        microservice_id = service_dict['ServiceID']
        container_id = service_dict['container_id']
        microservice_start_timestamp = service_dict['start_timestamp']
        single_active_instance = service_dict.get('single_active_instance', False)
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
            result[microservice_id] = microservice_dict
    return result


def _choose_active_instances(services_dicts):
    result = services_dicts
    running_services_with_single_active_instances = {}
    for microservice_id, service_dict in services_dicts.items():
        if service_dict.get('single_active_instance') and service_dict['status'] in ('passing', 'warning'):
            key = 'chosen_active_instance/{},env={},app_id={}'.format(service_dict['name'],
                                                                      service_dict['tags'].get('env') or '',
                                                                      service_dict['tags'].get('app_id') or '')
            if key not in running_services_with_single_active_instances:
                running_services_with_single_active_instances[key] = set()
            running_services_with_single_active_instances[key].add(microservice_id)

    for key, running_microservice_ids in running_services_with_single_active_instances.items():
        currently_picked_instance = kv.kv_get(key)
        if currently_picked_instance not in running_microservice_ids:
            currently_picked_instance = random.choice(list(running_microservice_ids))
            kv.kv_set(key, currently_picked_instance)
        for microservice_id in running_microservice_ids:
            if microservice_id != currently_picked_instance:
                result[microservice_id]['status'] = 'standby'
    return result
