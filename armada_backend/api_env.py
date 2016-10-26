from armada_backend import api_base, docker_client


class GetEnv(api_base.ApiCommand):
    def GET(self, container_id, key):
        try:
            docker_api = docker_client.api()
            docker_inspect = docker_api.inspect_container(container_id)
            value = None
            for env_var in docker_inspect['Config']['Env']:
                env_key, env_value = (env_var.strip('"').split('=', 1) + [''])[:2]
                if env_key == key:
                    value = env_value
                    break

            if value is None:
                return self.status_error('Requested environment variable "{key}" does not exist.'.format(**locals()))
            return self.status_ok({'value': str(value)})
        except Exception as e:
            return self.status_exception("Cannot inspect requested container.", e)
