from armada_backend import api_base, docker_client


def get_env(container_id, key):
    docker_api = docker_client.api()
    docker_inspect = docker_api.inspect_container(container_id)
    for env_var in docker_inspect['Config']['Env']:
        env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
        if env_key == key:
            return env_value
    return None


class GetEnv(api_base.ApiCommand):
    def on_get(self, req, resp, container_id, key):
        try:
            value = get_env(container_id, key)

            if value is None:
                return self.status_error(resp,
                                         'Requested environment variable "{key}" does not exist.'.format(**locals()))
            return self.status_ok(resp, {'value': str(value)})
        except Exception as e:
            return self.status_exception(resp, "Cannot inspect requested container.", e)
