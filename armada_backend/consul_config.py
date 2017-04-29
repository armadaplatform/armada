from armada_command.scripts.compat import json

CONFIG_PATH = '/etc/consul.config'

# File where runtime settings are saved after something changes.
RUNTIME_SETTINGS_PATH = '/opt/armada/runtime_settings.json'
# Runtime settings at the time of last consul start/restart.
ORIGINAL_RUNTIME_SETTINGS_PATH = '/tmp/original_runtime_settings.json'
# Changes to be applied after next consul restart.
OVERRIDE_RUNTIME_SETTINGS_PATH = '/tmp/override_runtime_settings.json'
# Container parameters saved for recovery after Docker daemon restart.
RUNNING_CONTAINERS_PARAMETERS_PATH = '/opt/armada/running_containers_parameters.json'


def enum(**enums):
    return type('Enum', (), enums)


ConsulMode = enum(BOOTSTRAP=0, SERVER=1, CLIENT=2)


def get_consul_config(consul_mode, ship_ips, datacenter, ship_external_ip, ship_name):
    is_server = (consul_mode != ConsulMode.CLIENT)
    config = {
        'server': is_server,
        'start_join': ship_ips,
        'datacenter': str(datacenter),
        'node_name': 'ship-{0}'.format(ship_external_ip),
        'advertise_addr': str(ship_external_ip),
        'client_addr': '0.0.0.0',
        'data_dir': '/var/opt/consul-{datacenter}-{consul_mode}'.format(**locals()),
        'leave_on_terminate': True,
        'performance': {'raft_multiplier': 1},
    }

    if consul_mode == ConsulMode.BOOTSTRAP:
        config['bootstrap_expect'] = 1

    env_pythonpath = 'PYTHONPATH=/opt/armada-docker:$PYTHONPATH'

    save_runtime_settings_cmd = '{env_pythonpath} python -m armada_backend.runtime_settings'.format(**locals())
    running_containers_parameters_path = RUNNING_CONTAINERS_PARAMETERS_PATH
    save_running_containers_cmd = ('{env_pythonpath} python -m armada_backend.save_running_containers '
                                   '{running_containers_parameters_path} '
                                   '>> /tmp/save_running_containers.out 2>&1').format(**locals())
    config['watches'] = [
        {'type': 'keyprefix', 'prefix': 'dockyard/', 'handler': save_runtime_settings_cmd},
        {'type': 'nodes', 'handler': save_runtime_settings_cmd},
        {'type': 'keyprefix', 'prefix': 'ships/{}/'.format(ship_name), 'handler': save_running_containers_cmd},
    ]

    return json.dumps(config, sort_keys=True, indent=4)
