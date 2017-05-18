import base64
from armada_command.scripts.compat import json

import web

from armada_backend import api_base, docker_client
from armada_backend.api_run_hermes import process_hermes
from armada_backend.utils import get_logger
from armada_command.armada_utils import split_image_path
from armada_command.dockyard.alias import INSECURE_REGISTRY_ERROR_MSG
from armada_command.ship_config import get_ship_config


class Create(api_base.ApiCommand):
    def _create_service(self, image_path=None, microservice_name=None, microservice_env=None, microservice_app_id=None,
                        dockyard_user=None, dockyard_password=None, ports=None, environment=None, volumes=None,
                        run_command=None, resource_limits=None, configs=None, **kwargs):
        # Check required fields in received JSON:
        if not image_path:
            raise ValueError('Field image_path cannot be empty.')
        if not run_command:
            raise ValueError('Field run_command cannot be empty.')

        if kwargs:
            get_logger().warning('JSON data sent to API contains unrecognized keys: %s', list(kwargs.keys()))

        # Set default values:
        environment = environment or {}
        ports = ports or {}
        volumes = volumes or {}
        resource_limits = resource_limits or {}
        configs = configs or []
        image_name = split_image_path(image_path)[1]
        microservice_name = microservice_name or environment.get('MICROSERVICE_NAME') or image_name
        microservice_env = microservice_env or environment.get('MICROSERVICE_ENV')
        microservice_app_id = microservice_app_id or environment.get('MICROSERVICE_APP_ID')

        # Update environment variables with armada-specific values:
        restart_parameters = {
            'image_path': image_path,
            'microservice_name': microservice_name,
            'microservice_env': microservice_env,
            'microservice_app_id': microservice_app_id,
            'dockyard_user': dockyard_user,
            'dockyard_password': dockyard_password,
            'ports': ports,
            'environment': environment,
            'volumes': volumes,
            'run_command': run_command,
            'resource_limits': resource_limits,
            'configs': configs,
        }

        dev = environment.get('ARMADA_VAGRANT_DEV')
        if dev:
            restart_parameters['image_path'] = image_path.split('/', 1)[-1]

        environment['RESTART_CONTAINER_PARAMETERS'] = base64.b64encode(json.dumps(restart_parameters, sort_keys=True))
        environment['ARMADA_RUN_COMMAND'] = base64.b64encode(run_command)
        environment['MICROSERVICE_NAME'] = microservice_name
        if microservice_env:
            environment['MICROSERVICE_ENV'] = microservice_env
        if microservice_app_id:
            environment['MICROSERVICE_APP_ID'] = microservice_app_id
        config_path, hermes_volumes = process_hermes(microservice_name, image_name, microservice_env,
                                                     microservice_app_id, configs)
        if config_path:
            environment['CONFIG_PATH'] = config_path

        volumes[docker_client.DOCKER_SOCKET_PATH] = docker_client.DOCKER_SOCKET_PATH
        volumes.update(hermes_volumes or {})
        long_container_id = self._create_container(
            image_path, microservice_name, ports, environment, volumes,
            dockyard_user, dockyard_password, resource_limits)
        return long_container_id

    def _create_container(self, image_path, microservice_name, dict_ports, dict_environment, dict_volumes,
                          dockyard_user, dockyard_password, resource_limits):
        ports = None
        port_bindings = None
        if dict_ports:
            ports = map(int, dict_ports.values())
            port_bindings = dict((int(port_container), int(port_host))
                                 for port_host, port_container in dict_ports.iteritems())

        environment = dict_environment or None

        volumes = None
        volume_bindings = None
        if dict_volumes:
            volumes = dict_volumes.values()
            volume_bindings = dict(
                (path_host, {'bind': path_container, 'ro': False}) for path_host, path_container in
                dict_volumes.iteritems())

        dockyard_address, image_name, image_tag = split_image_path(image_path)
        docker_api = self._get_docker_api(dockyard_address, dockyard_user, dockyard_password)
        self._pull_latest_image(docker_api, image_path)
        dev = environment.get('ARMADA_VAGRANT_DEV')
        if dev:
            self._tag_local_image(docker_api, image_path)
            image_path = '{}:{}'.format(image_name, image_tag)

        host_config = self._create_host_config(docker_api, resource_limits, volume_bindings, port_bindings)
        container_info = docker_api.create_container(image_path,
                                                     ports=ports,
                                                     environment=environment,
                                                     volumes=volumes,
                                                     host_config=host_config)
        long_container_id = container_info['Id']
        return long_container_id

    def _login_to_dockyard(self, docker_api, dockyard_address, dockyard_user, dockyard_password):
        if dockyard_user and dockyard_password:
            logged_in = False
            # Workaround for abrupt changes in docker-py library.
            login_exceptions = []
            registry_endpoints = [
                'https://{0}/v1/'.format(dockyard_address),
                'https://{0}'.format(dockyard_address),
                dockyard_address
            ]
            for registry_endpoint in registry_endpoints:
                try:
                    docker_api.login(dockyard_user, dockyard_password, registry=registry_endpoint)
                    logged_in = True
                    break
                except Exception as e:
                    get_logger().debug(e)
                    login_exceptions.append(e)

            if not logged_in:
                raise login_exceptions[0]

    def _get_docker_api(self, dockyard_address, dockyard_user, dockyard_password):
        docker_api = docker_client.api(timeout=30)
        self._login_to_dockyard(docker_api, dockyard_address, dockyard_user, dockyard_password)
        return docker_api

    def _pull_latest_image(self, docker_api, image_path):
        dockyard_address, image_name, image_tag = split_image_path(image_path)
        if dockyard_address:
            try:
                docker_client.docker_pull(docker_api, dockyard_address, image_name, image_tag)
            except Exception as e:
                if "ping attempt failed" in str(e):
                    raise RuntimeError(INSECURE_REGISTRY_ERROR_MSG.format(header="ERROR!", address=dockyard_address))
                raise e

    def _tag_local_image(self, docker_api, image_path):
        dockyard_address, image_name, image_tag = split_image_path(image_path)
        if dockyard_address:
            docker_client.docker_tag(docker_api, dockyard_address, image_name, image_tag)

    def _create_host_config(self, docker_api, resource_limits, binds, port_bindings):
        resource_limits = resource_limits or {}
        privileged = get_ship_config().get('privileged', 'false').lower() == 'true'
        host_config = docker_api.create_host_config(
            privileged=privileged,
            publish_all_ports=True,
            binds=binds,
            port_bindings=port_bindings,
            mem_limit=resource_limits.get('memory'),
            memswap_limit=resource_limits.get('memory_swap'),
            cgroup_parent=resource_limits.get('cgroup_parent'),
        )
        host_config['CpuShares'] = resource_limits.get('cpu_shares')
        return host_config

    def POST(self):
        try:
            post_data = json.loads(web.data())
        except Exception as e:
            return self.status_exception('API Run: Invalid input JSON.', e)

        try:
            long_container_id = self._create_service(**post_data)
            return self.status_ok({'long_container_id': long_container_id})
        except Exception as e:
            return self.status_exception("Cannot create service's container.", e)
