import sys
from armada_command.armada_utils import ArmadaCommandException
from armada_command.command_run_hermes import process_hermes
from armada_command.dockyard import dockyard

class RunPayload:
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
                raise ArmadaCommandException("Couldn't read configuration for dockyard alias {0}.".format(dockyard_alias))
            self._payload['dockyard_user'] = dockyard_info.get('user'),
            self._payload['dockyard_password'] = dockyard_info.get('password')

    def update_vagrant(self, dynamic_ports, latest_image_code, microservice_name):
        if not dynamic_ports:
            self._payload['ports']['4999'] = '80'
        if not latest_image_code:
            microservice_path = '/opt/{microservice_name}'.format(**locals())
            self._payload['volumes'][microservice_path] = microservice_path
        self._payload['environment']['ARMADA_VAGRANT_DEV'] = '1'

    def update_hermes(self, image_name, env, app_id, configs,):
        hermes_env, hermes_volumes = process_hermes(image_name, env, app_id,
                                                    sum(configs or [], []))
        self._payload['environment'].update(hermes_env or {})
        self._payload['volumes'].update(hermes_volumes or {})

    def update_environment(self, env_vars):
        for env_var in sum(env_vars or [], []):
            env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
            self._payload['environment'][env_key] = env_value

    def update_ports(self, ports):
        for port_mapping in sum(ports or [], []):
            try:
                port_host, port_container = map(int, (port_mapping.split(':', 1) + [None])[:2])
                self._payload['ports'][str(port_host)] = str(port_container)
            except (ValueError, TypeError):
                raise ArmadaCommandException('Invalid port mapping: {0}'.format(port_mapping))

    def update_volumes(self, volumes):
        for volume_string in sum(volumes or [], []):
            volume = volume_string.split(':')
            if len(volume) == 1:
                volume *= 2
            self._payload['volumes'][volume[0]] = volume[1]

    def update_microservice_name(self, name):
        self._payload['microservice_name'] = name

    def update_run_command(self, vagrant_dev):
        run_command = 'armada ' + ' '.join(sys.argv[1:])
        if vagrant_dev and '--hidden_vagrant_dev' not in run_command:
            run_command += ' --hidden_vagrant_dev'
        if '--hidden_is_restart' not in run_command:
            run_command += ' --hidden_is_restart'
        self._payload['run_command'] = run_command


