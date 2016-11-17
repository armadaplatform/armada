import os

ARMADA_CONFIG_FILE_PATH = '/etc/default/armada'


def get_ship_config():
    result = {}
    if not os.path.exists(ARMADA_CONFIG_FILE_PATH):
        return result
    with open(ARMADA_CONFIG_FILE_PATH) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, value = line.split('=', 1)
        result[key.strip()] = value.strip().strip('\'"')
    return result
