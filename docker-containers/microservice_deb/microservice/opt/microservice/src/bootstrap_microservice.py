import os


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


def main():
    if "CONFIG_DIR" in os.environ:
        service_path = os.path.join("/opt", os.environ["MICROSERVICE_NAME"])
        config_dir = os.environ["CONFIG_DIR"]
        microservice_env = os.environ.get("MICROSERVICE_ENV", '')
        microservice_app_id = os.environ.get("MICROSERVICE_APP_ID", '')

        config_dirs_combinations = set(_get_all_parent_dirs_with_combinations(microservice_env, microservice_app_id))

        config_dirs_full_paths = [os.path.join(service_path, config_dir, path) for path in config_dirs_combinations]
        config_dirs_full_paths.sort(key=_nesting_level, reverse=True)
        config_dirs_existing_paths = filter(os.path.isdir, config_dirs_full_paths)

        local_config_path = os.pathsep.join(config_dirs_existing_paths)

        if "CONFIG_PATH" in os.environ:
            os.environ["CONFIG_PATH"] = os.environ["CONFIG_PATH"] + os.pathsep + local_config_path
        else:
            os.environ["CONFIG_PATH"] = local_config_path

    supervisor_cmd = "/usr/bin/supervisord"
    os.execv(supervisor_cmd, (supervisor_cmd, "-c", "/etc/supervisor/supervisord.conf"))


if __name__ == '__main__':
    main()
