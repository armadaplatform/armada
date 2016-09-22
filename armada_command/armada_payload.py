import sys

from armada_command.armada_utils import ArmadaCommandException
from armada_command.dockyard import dockyard


class RunPayload(object):
    def __init__(self):
        self._payload = {'environment': {}, 'ports': {}, 'volumes': {}}

    def __str__(self):
        return str(self._payload)

    def get(self, key):
        return self._payload.get(key)

    def data(self):
        return self._payload

    def update_image_path(self, image_path):
        self._payload['image_path'] = image_path

    def update_dockyard(self, dockyard_alias):
        if dockyard_alias and dockyard_alias != 'local':
            dockyard_info = dockyard.alias.get_alias(dockyard_alias)
            if not dockyard_info:
                raise ArmadaCommandException(
                    "Couldn't read configuration for dockyard alias {0}.".format(dockyard_alias))
            self._payload['dockyard_user'] = dockyard_info.get('user')
            self._payload['dockyard_password'] = dockyard_info.get('password')

    def update_vagrant(self, has_dynamic_ports, ports, latest_image_code, microservice_name):
        is_port_80_overridden = any(port_container == 80 for _, port_container in self._ports_to_mapping_dict(ports).items())

        if not (has_dynamic_ports or is_port_80_overridden):
            self._payload['ports']['4999'] = '80'
        if not latest_image_code:
            microservice_path = '/opt/{microservice_name}'.format(**locals())
            self._payload['volumes'][microservice_path] = microservice_path
        self._payload['environment']['ARMADA_VAGRANT_DEV'] = '1'

    def update_environment(self, env_vars):
        for env_var in sum(env_vars or [], []):
            env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
            self._payload['environment'][env_key] = env_value

    def update_ports(self, ports):
        for port_host, port_container in self._ports_to_mapping_dict(ports).items():
            self._payload['ports'][str(port_host)] = str(port_container)

    def update_volumes(self, volumes):
        for volume_string in sum(volumes or [], []):
            volume = volume_string.split(':')
            if len(volume) == 1:
                volume *= 2
            self._payload['volumes'][volume[0]] = volume[1]

    def update_microservice_vars(self, name, env, app_id):
        self._payload['microservice_name'] = name
        self._payload['microservice_env'] = env
        self._payload['microservice_app_id'] = app_id

    def update_run_command(self, vagrant_dev, env, name):
        run_command = 'armada ' + ' '.join(sys.argv[1:])
        if vagrant_dev and '--hidden_vagrant_dev' not in run_command:
            run_command += ' --hidden_vagrant_dev'
        if '--hidden_is_restart' not in run_command:
            run_command += ' --hidden_is_restart'
        if env and '--env' not in run_command:
            run_command += ' --env {env}'.format(**locals())
        if name not in run_command:
            run_command += ' {name}'.format(**locals())
        self._payload['run_command'] = run_command

    def update_resource_limits(self, cpu_shares, memory, memory_swap, cgroup_parent):
        resource_limits = {}
        if cpu_shares:
            resource_limits['cpu_shares'] = cpu_shares
        if memory:
            resource_limits['memory'] = memory
        if memory_swap:
            resource_limits['memory_swap'] = memory_swap
        if cgroup_parent:
            resource_limits['cgroup_parent'] = cgroup_parent
        self._payload['resource_limits'] = resource_limits

    def update_configs(self, configs):
        self._payload['configs'] = sum(configs or [], [])

    def _ports_to_mapping_dict(self, ports):
        mapping_dict = {}
        for port_mapping in sum(ports or [], []):
            try:
                port_host, port_container = map(int, (port_mapping.split(':', 1) + [None])[:2])
                mapping_dict[port_host] = port_container
            except (ValueError, TypeError):
                raise ArmadaCommandException('Invalid port mapping: {0}'.format(port_mapping))
        return mapping_dict
