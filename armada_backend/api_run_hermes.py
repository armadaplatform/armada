import itertools
import os

CONFIGS_CUSTOM_DIR = '/configs/'
CONFIG_PATH_BASE = '/etc/opt/'
RESTRICT_CUSTOM_CONFIG_DIRS = os.environ.get('RESTRICT_CUSTOM_CONFIG_DIRS', '').rstrip('/') + '/'

class Volumes(object):
    def __init__(self):
        self.volumes = []

    def add_config_paths(self, config_paths):
        for config_path in config_paths:
            # os.path.join ignores CONFIG_PATH_BASE if config_path is an absolute path!
            volume_path = os.path.join(CONFIG_PATH_BASE, config_path)
            self.volumes.append(volume_path)

    def get_existing_volumes(self):
        used = set()
        for volume in self.volumes:
            if volume in used:
                continue

            if volume.startswith(CONFIG_PATH_BASE):
                if _is_directory(volume, host_path=CONFIG_PATH_BASE, container_path=CONFIG_PATH_BASE):
                    used.add(volume)
                    yield volume
                continue

            if volume.startswith(RESTRICT_CUSTOM_CONFIG_DIRS):
                if _is_directory(volume, host_path=RESTRICT_CUSTOM_CONFIG_DIRS, container_path=CONFIGS_CUSTOM_DIR):
                    used.add(volume)
                    yield volume
                continue

            raise Exception("{0} is outside of allowed config mount points. ({1}, {2})".
                            format(volume, CONFIG_PATH_BASE, RESTRICT_CUSTOM_CONFIG_DIRS))


def _is_directory(path, host_path='/', container_path='/'):
    """
    Checks if given path is a directory. It is a generalized version of os.path.isdir() that can work with changed
    root directory, even if the `path` contains symlinks.
    """
    if not path.startswith(host_path):
        return False

    path = path[len(host_path):]
    path_so_far = container_path
    for directory in path.lstrip('/').split('/'):
        rooted_path = os.path.join(path_so_far, directory)
        while os.path.islink(rooted_path):
            link_destination = os.readlink(rooted_path)
            if os.path.isabs(link_destination):
                if not link_destination.startswith(host_path):
                    return False
                rooted_path = os.path.join(container_path, link_destination[len(host_path):].lstrip('/'))
            else:
                rooted_path = os.path.join(rooted_path, os.path.pardir, link_destination)
        if not os.path.isdir(rooted_path):
            return False
        path_so_far = rooted_path
    return True


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


def _create_service_relative_config_paths(microservice_name, app_id, environments_dirs):
    result = []
    microservice_configs = ['{0}-config-secret'.format(microservice_name), '{0}-config'.format(microservice_name),
                            microservice_name]
    if app_id:
        app_configs = ['{0}-config-secret'.format(app_id), '{0}-config'.format(app_id), app_id]
        result.extend(_generate_paths_from_all_combinations(app_configs, [microservice_name], environments_dirs))
        result.extend(_generate_paths_from_all_combinations(app_configs, environments_dirs, [microservice_name]))
        result.extend(_generate_paths_from_all_combinations(microservice_configs, environments_dirs, [app_id]))
        result.extend(_generate_paths_from_all_combinations(microservice_configs, [app_id], environments_dirs))
    result.extend(_generate_paths_from_all_combinations(microservice_configs, environments_dirs))
    return result


def process_hermes(microservice_name, image_name, env, app_id, configs):
    environments_dirs = _get_environments_dirs(env or '')

    possible_config_paths = []
    if configs:
        if app_id:
            possible_config_paths.extend(_generate_paths_from_all_combinations(configs, environments_dirs, [app_id]))
            possible_config_paths.extend(_generate_paths_from_all_combinations(configs, [app_id], environments_dirs))
        possible_config_paths.extend(_generate_paths_from_all_combinations(configs, environments_dirs))
    if microservice_name:
        possible_config_paths.extend(_create_service_relative_config_paths(
            microservice_name, app_id, environments_dirs))
    if image_name:
        possible_config_paths.extend(_create_service_relative_config_paths(
            image_name, app_id, environments_dirs))

    volumes = Volumes()
    volumes.add_config_paths(possible_config_paths)
    existing_volumes = list(volumes.get_existing_volumes())

    config_path = os.pathsep.join(existing_volumes)
    hermes_volumes = {volume: volume for volume in existing_volumes}

    return config_path, hermes_volumes
