import fnmatch
from distutils.util import strtobool

import web
from armada_backend import api_base
from armada_backend.utils import get_ship_name, get_ship_names
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
                        try:
                            microservice_start_timestamp = kv.kv_get("start_timestamp/" + container_id)
                        except:
                            microservice_start_timestamp = None
                        microservice_dict = {
                            'name': microservice_name,
                            'address': microservice_address,
                            'microservice_id': microservice_id,
                            'container_id': container_id,
                            'status': microservice_computed_status,
                            'tags': microservice_tags_dict,
                            'start_timestamp': microservice_start_timestamp,
                        }
                        services_list_from_catalog[microservice_id] = microservice_dict

            result = services_list
            result.update(services_list_from_catalog)
            return self.status_ok({'result': result.values()})
        except Exception as e:
            return self.status_exception("Cannot get the list of services.", e)


def _get_services_list(filter_microservice_name, filter_env, filter_app_id, filter_local):
    if filter_local:
        ship_list = [get_ship_name()]
    else:
        ship_list = get_ship_names()
    services_dict = {}
    if not ship_list:
        return {}
    for ship in ship_list:
        containers = kv.kv_get('containers_parameters_list/{}'.format(ship))
        if containers and isinstance(containers, dict):
            services_dict.update(containers)

    services_list = services_dict.keys()

    result = {}
    if not services_list:
        return result

    if filter_microservice_name:
        services_list = fnmatch.filter(services_list, 'ships/*/service/{}/*'.format(filter_microservice_name))

    for service in services_list:
        service_dict = services_dict[service]
        microservice_name = service_dict['ServiceName']
        microservice_status = service_dict['Status']
        microservice_id = service_dict['ServiceID']
        container_id = service_dict['container_id']
        microservice_start_timestamp = service_dict['start_timestamp']
        not_available = 'n/a'

        microservice_tags_dict = {}
        if service_dict['params']['microservice_env']:
            microservice_tags_dict['env'] = service_dict['params']['microservice_env']
        if service_dict['params']['microservice_app_id']:
            microservice_tags_dict['app_id'] = service_dict['params']['microservice_app_id']

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
            }
            result[microservice_id] = microservice_dict
    return result
