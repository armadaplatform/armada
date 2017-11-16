import os
import random
import shutil

from armada_backend import consul_config
from armada_backend.utils import get_logger, setup_sentry, get_external_ip
from armada_command.scripts.compat import json


def _get_runtime_settings():
    try:
        shutil.copy(consul_config.RUNTIME_SETTINGS_PATH, consul_config.ORIGINAL_RUNTIME_SETTINGS_PATH)
        with open(consul_config.ORIGINAL_RUNTIME_SETTINGS_PATH) as runtime_settings_json:
            runtime_settings = json.load(runtime_settings_json)
    except:
        runtime_settings = {}

    try:
        with open(consul_config.OVERRIDE_RUNTIME_SETTINGS_PATH) as runtime_settings_json:
            runtime_settings.update(json.load(runtime_settings_json))
    except:
        pass

    ship_ips = runtime_settings.get('ships', [])
    consul_mode = consul_config.ConsulMode.BOOTSTRAP
    if runtime_settings.get('is_commander') is True:
        if ship_ips and len(ship_ips) > 0:
            consul_mode = consul_config.ConsulMode.SERVER
    if runtime_settings.get('is_commander') is False:
        consul_mode = consul_config.ConsulMode.CLIENT

    if runtime_settings.get('datacenter'):
        datacenter = runtime_settings.get('datacenter')
    else:
        datacenter = 'dc-' + str(random.randrange(1000000))

    ship_name = runtime_settings.get('name')

    return consul_mode, ship_ips, datacenter, ship_name


def main():
    setup_sentry()
    consul_mode, ship_ips, datacenter, ship_name = _get_runtime_settings()
    ship_external_ip = get_external_ip()
    if ship_name is None:
        ship_name = ship_external_ip

    consul_config_dict = consul_config.get_consul_config(consul_mode, ship_ips, datacenter, ship_external_ip, ship_name)

    data_dir = consul_config_dict['data_dir']
    print(data_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(os.path.join(data_dir, 'dummy'), 'w') as f:
        f.write('')

    consul_config_content = json.dumps(consul_config_dict, sort_keys=True, indent=4)
    with open(consul_config.CONFIG_PATH, 'w') as config_file:
        config_file.write(consul_config_content)

    command = ['consul', 'agent', '-config-file', consul_config.CONFIG_PATH, '-data-dir', data_dir]
    get_logger().info('RUNNING: %s', ' '.join(command))

    os.execvp(command[0], command)


if __name__ == '__main__':
    main()
