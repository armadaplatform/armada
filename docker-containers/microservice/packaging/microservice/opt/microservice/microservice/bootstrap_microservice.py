from __future__ import print_function

import os
import sys

from microservice.save_environment_variables import save_environment_variables


def _get_all_parent_dirs(path):
    while True:
        parent, base = os.path.split(path)
        if base:
            yield path
        if not parent or path == parent:
            break
        path = parent
    yield ''


def _get_all_parent_dirs_with_combinations(path_1, path_2):
    for path in _get_all_parent_dirs(os.path.join(path_1, path_2)):
        yield path

    for path in _get_all_parent_dirs(os.path.join(path_2, path_1)):
        yield path

    for path in _get_all_parent_dirs(path_1):
        yield path

    for path in _get_all_parent_dirs(path_2):
        yield path


def _nesting_level(path):
    return path.rstrip('/').count('/')


def _generate_config_full_path(base_path, config_dir, config_dirs_combinations):
    image_config_dirs = [os.path.join(base_path, config_dir, path) for path in config_dirs_combinations]
    image_config_dirs.sort(key=_nesting_level, reverse=True)
    return image_config_dirs


def main():
    if "CONFIG_DIR" in os.environ:
        service_path = os.path.join("/opt", os.environ["MICROSERVICE_NAME"])
        config_dir = os.environ["CONFIG_DIR"]
        microservice_env = os.environ.get("MICROSERVICE_ENV", '')
        microservice_app_id = os.environ.get("MICROSERVICE_APP_ID", '')

        config_dirs_combinations = set(_get_all_parent_dirs_with_combinations(microservice_env, microservice_app_id))
        service_config_dirs_full_paths = _generate_config_full_path(service_path, config_dir, config_dirs_combinations)

        if os.environ.get("IMAGE_NAME") != os.environ["MICROSERVICE_NAME"]:
            image_path = os.path.join("/opt", os.environ["IMAGE_NAME"])
            image_config_dirs = _generate_config_full_path(image_path, config_dir, config_dirs_combinations)
            service_config_dirs_full_paths.extend(image_config_dirs)

        config_dirs_existing_paths = list(filter(os.path.isdir, service_config_dirs_full_paths))

        local_config_path = os.pathsep.join(config_dirs_existing_paths)

        if "CONFIG_PATH" in os.environ:
            os.environ["CONFIG_PATH"] = os.environ["CONFIG_PATH"] + os.pathsep + local_config_path
        else:
            os.environ["CONFIG_PATH"] = local_config_path

    save_environment_variables()
    supervisor_cmd = "supervisord"
    os.execvp(supervisor_cmd, (supervisor_cmd, "-c", "/etc/supervisor/supervisord.conf"))


if __name__ == '__main__':
    print('WARNING: Calling this script directly has been deprecated. Try `microservice bootstrap` instead.',
          file=sys.stderr)
    main()
