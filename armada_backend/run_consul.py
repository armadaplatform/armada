import subprocess
import os
import shutil
import random
import json

import consul_config


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

    if runtime_settings.get('name'):
        ship_name = runtime_settings.get('name')
    else:
        ship_name = os.environ.get('SHIP_EXTERNAL_IP', '')

    ship_ips = runtime_settings.get('ships', [])
    consul_mode = consul_config.ConsulMode.BOOTSTRAP
    if runtime_settings.get('is_commander') == True:
        if ship_ips and len(ship_ips) > 0:
            consul_mode = consul_config.ConsulMode.SERVER
    if runtime_settings.get('is_commander') == False:
        consul_mode = consul_config.ConsulMode.CLIENT

    if runtime_settings.get('datacenter'):
        datacenter = runtime_settings.get('datacenter')
    else:
        datacenter = 'dc-' + str(random.randrange(1000000))

    return ship_name, consul_mode, ship_ips, datacenter


def main():
    ship_name, consul_mode, ship_ips, datacenter = _get_runtime_settings()
    ship_external_ip = os.environ.get('SHIP_EXTERNAL_IP', '')
    consul_config_content = consul_config.get_consul_config(**locals())

    with open(consul_config.CONFIG_PATH, 'w') as config_file:
        config_file.write(consul_config_content)

    command = 'consul agent -config-file {config_path}'.format(config_path=consul_config.CONFIG_PATH)
    print 'RUNNING: ' + command

    with open('/tmp/consul.log', 'a') as output_f:
        subprocess.call(command.split(), stdout=output_f, stderr=output_f)

if __name__ == '__main__':
    main()
