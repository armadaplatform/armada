from __future__ import print_function
import os, sys


EXCLUDED_ENVIRONMENT_KEYS = {
    'PATH',
    'HOME',
    'SUPERVISOR_GROUP_NAME',
    'SUPERVISOR_ENABLED',
    'SUPERVISOR_PROCESS_NAME',
    'SUPERVISOR_SERVER_URL'
}
EXCLUDED_ENVIRONMENT_KEYS_FROM_CRONTAB = {
    'RESTART_CONTAINER_PARAMETERS',
    'ARMADA_RUN_COMMAND',
    'MICROSERVICE_FORCE_APT_GET_UPDATE'
}
BASHRC_PATH = '/etc/bash.bashrc'
ARMADA_ENVIRONMENT_VARIABLES_PATH = '/var/opt/armada_environment.sh'
ARMADA_ENVIRONMENT_VARIABLES_EXPORT_PATH = '/var/opt/armada_environment_export.sh'


def parse_environment_variables(environment_variables):
    for env_var in environment_variables:
        env_key, env_val = env_var.split('=', 1)
        yield env_key, env_val


def exclude_environment_variables(environment_keys_values, excluded):
    return filter(lambda env_var: env_var[0] not in excluded, environment_keys_values)


def add_environment_variables_to_bashrc(environment_variables_export_path, bashrc_path):
    with open(bashrc_path, 'a') as bashrc:
        line = 'source {environment_variables_export_path}\n'.format(**locals())
        bashrc.write(line)


def create_safe_env_var_definition(env_key, env_val):
    return '{env_key}="{env_val}"'.format(**locals())


def create_armada_environment_variables_file(environment_keys_values, environment_variables_path):
    with open(environment_variables_path, 'w') as environment_variables_file:
        for env_key, env_val in environment_keys_values:
            safe_env_var = create_safe_env_var_definition(env_key, env_val)
            environment_variables_file.write(safe_env_var + '\n')


def create_armada_environment_variables_export_file(environment_keys_values, environment_variables_export_path):
    with open(environment_variables_export_path, 'w') as environment_variables_export_file:
        for env_key, env_val in environment_keys_values:
            safe_env_var = 'export ' + create_safe_env_var_definition(env_key, env_val)
            environment_variables_export_file.write(safe_env_var + '\n')


def add_environment_variables_to_crontab(environment_keys_values):
    for env_key, env_val in environment_keys_values:
        safe_env_var = create_safe_env_var_definition(env_key, env_val)
        command = '(echo \'{0}\'; crontab -l) | crontab -'.format(safe_env_var)
        if os.system(command) != 0:
            print('Following environment variable could not have been added to crontab, possibly because of '
                  'hitting crontab\'s 1000 characters limit per line:\n{0}'.format(safe_env_var), file=sys.stderr)


def main():
    environment_keys_values = [(key, os.environ[key]) for key in os.environ if key not in EXCLUDED_ENVIRONMENT_KEYS]

    create_armada_environment_variables_file(environment_keys_values,
                                             ARMADA_ENVIRONMENT_VARIABLES_PATH)
    create_armada_environment_variables_export_file(environment_keys_values,
                                                    ARMADA_ENVIRONMENT_VARIABLES_EXPORT_PATH)

    add_environment_variables_to_bashrc(ARMADA_ENVIRONMENT_VARIABLES_EXPORT_PATH, BASHRC_PATH)

    environment_keys_values_filtered_for_crontab = exclude_environment_variables(environment_keys_values,
                                                                                 EXCLUDED_ENVIRONMENT_KEYS_FROM_CRONTAB)
    add_environment_variables_to_crontab(environment_keys_values_filtered_for_crontab)


if __name__ == '__main__':
    main()
