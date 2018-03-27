import os
from armada import hermes


def main():

    config = hermes.get_config('config.json', {})

    if not config.get('use_apache', False):
        os.environ["FLASK_APP"] = "main.py"
        os.environ["FLASK_DEBUG"] = "1"

        os.chdir("/opt/{0}/src".format(os.environ.get("MICROSERVICE_NAME", "")))
        command = "python3 -m flask run --port 80 --host 0.0.0.0"
        args = command.split()
        os.execvp(args[0], args)

    else:
        with open("/etc/apache2/envvars", "a") as f:
            for env_var in ['MICROSERVICE_NAME', 'MICROSERVICE_ENV', 'MICROSERVICE_APP_ID', 'CONFIG_PATH']:
                f.write("export {env_var}=\"{env_value}\"\n".format(env_var=env_var, env_value=os.environ.get(env_var, "")))

        apache_config = config.get('apache_config', {})
        if apache_config:
            with open("/etc/apache2/defines.conf", "w") as f:
                for k, v in apache_config.items():
                    f.write("Define {key} {value}\n".format(key=k, value=v))

        command = "service apache2 start"
        args = command.split()
        os.execvp(args[0], args)


if __name__ == '__main__':
    main()
