import json
import os

import warnings

warnings.warn("Built-in hermes is deprecated. "
              "Up to date version can be downloaded with 'python3 -m pip install armada' "
              "and imported with 'from armada import hermes' statement.")


def get_config_file_path(key):
    for env in os.environ.get('CONFIG_PATH', '').split(os.pathsep):
        path = os.path.join(env, key)
        if os.path.exists(path):
            return path


def get_config(key, default=None, strip=True):
    path = get_config_file_path(key)
    if path is None:
        return default
    with open(path) as config_file:
        result = config_file.read()
    if strip:
        result = result.strip()
    if key.endswith('.json'):
        result = json.loads(result)
    return result


def get_configs(key, default=None, strip=True):
    path = get_config_file_path(key)
    if path is None or not os.path.isdir(path):
        return default
    result = {}
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            result[file_name] = get_config(os.path.join(key, file_name), strip)
    return result


def get_configs_keys(key, default=None):
    path = get_config_file_path(key)
    if path is None or not os.path.isdir(path):
        return default
    result = []
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            result.append(os.path.join(key, file_name))
    return result
