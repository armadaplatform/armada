import os
import itertools

CONFIG_PATH_BASE = '/etc/opt/'


class Volumes(object):
    def __init__(self):
        self.volumes = []

    def add_config_paths(self, config_paths):
        for config_path in config_paths:
            volume_mapping = (os.path.join(CONFIG_PATH_BASE, config_path),) * 2
            self.volumes.append(volume_mapping)

    def get_existing_volumes(self):
        used = set([])
        for volume in self.volumes:
            if os.path.isdir(volume[0]) and volume[1] not in used:
                used.add(volume[1])
                yield volume


def _get_all_subdirs(path):
    """Example: For path='prod/ext/test' it returns ['prod/ext/test', 'prod/ext', 'prod', '']"""
    while True:
        parent, base = os.path.split(path)
        if base:
            yield path
        if not parent or path == parent:
            break
        path = parent
    yield ''


def _get_environments_dirs(environment_string):
    environment_dirs = environment_string.split(os.pathsep)
    return [parent_dir for environment_dir in environment_dirs for parent_dir in _get_all_subdirs(environment_dir)]


def _generate_paths_from_all_combinations(*path_combinations):
    return (os.path.join(*path_elements) for path_elements in itertools.product(*path_combinations))


def _create_service_relative_config_paths(microservice_name, app_id, environment_dirs):
    result = []
    microservice_configs = ['{0}-config-secret'.format(microservice_name), '{0}-config'.format(microservice_name)]
    if app_id:
        app_configs = ['{0}-config-secret'.format(app_id), '{0}-config'.format(app_id)]
        result.extend(_generate_paths_from_all_combinations(app_configs, [microservice_name], environment_dirs))
        result.extend(_generate_paths_from_all_combinations(app_configs, environment_dirs, [microservice_name]))
        result.extend(_generate_paths_from_all_combinations(microservice_configs, environment_dirs, [app_id]))
        result.extend(_generate_paths_from_all_combinations(microservice_configs, [app_id], environment_dirs))
    result.extend(_generate_paths_from_all_combinations(microservice_configs, environment_dirs))
    return result


def process_hermes(microservice_name, env, app_id, configs):

    microservice_name = microservice_name.split(':', 1)[0]
    possible_config_paths = configs or []

    environments_dirs = _get_environments_dirs(env or '')
    possible_config_paths.extend(_create_service_relative_config_paths(microservice_name, app_id, environments_dirs))

    volumes = Volumes()
    volumes.add_config_paths(possible_config_paths)

    # --------------------------------------------------------------------------

    hermes_env = {}
    hermes_volumes = {}

    config_path = os.pathsep.join(volume[1] for volume in volumes.get_existing_volumes())
    if config_path:
        hermes_env['CONFIG_PATH'] = config_path
    if env:
        hermes_env['MICROSERVICE_ENV'] = env
    if app_id:
        hermes_env['MICROSERVICE_APP_ID'] = app_id

    for volume in volumes.get_existing_volumes():
        hermes_volumes[volume[0]] = volume[1]

    return hermes_env, hermes_volumes
