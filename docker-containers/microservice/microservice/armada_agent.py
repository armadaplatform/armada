from __future__ import print_function

import calendar
import glob
import json
import logging
import os
import random
import signal
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from functools import wraps, partial

import requests
from requests.exceptions import HTTPError

from microservice.common.consul import consul_query, consul_post, consul_get, consul_put
from microservice.common.docker_client import get_docker_inspect
from microservice.common.service_discovery import register_service_in_armada, register_service_in_armada_v1, \
    UnsupportedArmadaApiException
from microservice.defines import ARMADA_API_URL
from microservice.exceptions import ArmadaApiServiceNotFound
from microservice.register_in_service_discovery import REGISTRATION_DIRECTORY
from microservice.version import VERSION

HEALTH_CHECKS_PERIOD = 10
HEALTH_CHECKS_TIMEOUT = 10
HEALTH_CHECKS_PERIOD_VARIATION = 2
HEALTH_CHECKS_PERIOD_INCREMENTATION = 1
HEALTH_CHECKS_PATH_WILDCARD = '/opt/*/health-checks/*'


def print_err(*objs):
    print(*objs, file=sys.stderr)


def print_exc():
    traceback.print_exc()
    print_err()


def _exists_service(service_id):
    try:
        return service_id in consul_query('agent/services')
    except:
        return False


def _create_tags():
    tag_pairs = [
        ('env', os.environ.get('MICROSERVICE_ENV')),
        ('app_id', os.environ.get('MICROSERVICE_APP_ID')),
    ]
    return ['{k}:{v}'.format(**locals()) for k, v in tag_pairs if v]


def _register_service(consul_service_data):
    print_err('Registering service...')
    response = consul_post('agent/service/register', consul_service_data)
    assert response.status_code == requests.codes.ok
    print_err('Successfully registered.', '\n')


def _datetime_string_to_timestamp(datetime_string):
    # Converting "2014-12-11T09:24:13.852579969Z" to an epoch timestamp
    return calendar.timegm(datetime.strptime(
        datetime_string[:-4], "%Y-%m-%dT%H:%M:%S.%f").timetuple())


def _store_start_timestamp(container_id, container_created_timestamp):
    key = "kv/start_timestamp/" + container_id
    if consul_get(key).status_code == requests.codes.not_found:
        response = consul_put(key, str(container_created_timestamp))
        assert response.status_code == requests.codes.ok


def retry(num_retries, action=None, expected_exception=Exception):
    """
    it retries decorated function "num_retries" times
    and performs "action" after each "expected_exception" occurrence.
    """

    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            counter = 0
            while True:
                try:
                    return fun(*args, **kwargs)
                except expected_exception:
                    if counter >= num_retries:
                        raise
                    else:
                        print_exc()

                    if action:
                        action()

                    counter += 1

        return wrapper

    return decorator


@retry(num_retries=float('inf'), action=partial(time.sleep, 0.2))
def _wait_for_consul():
    agent_self_dict = consul_query('agent/self')
    if 'Config' not in agent_self_dict:
        raise Exception('Consul not ready yet')


def _walk_registration_files(directory):
    service_filename = os.environ['MICROSERVICE_NAME']
    files = next(os.walk(directory))[2]
    for filename in files:
        if filename.startswith(service_filename):
            yield os.path.join(directory, filename)


def _register_service_from_file(file_path):
    with open(file_path) as f:
        registration_service_data = json.load(f)

    service_id = registration_service_data['service_id']
    service_name = registration_service_data['service_name']
    service_local_port = registration_service_data['service_container_port']
    service_port = registration_service_data['service_port']
    single_active_instance = registration_service_data['single_active_instance']

    container_id = service_id.split(':')[0]
    docker_inspect = get_docker_inspect(container_id)
    container_created_timestamp = _datetime_string_to_timestamp(docker_inspect["Created"])

    try:
        register_service_in_armada_v1(service_id, service_name, service_local_port, os.environ.get('MICROSERVICE_ENV'),
                                      os.environ.get('MICROSERVICE_APP_ID'), container_created_timestamp,
                                      single_active_instance, VERSION)
        return
    except UnsupportedArmadaApiException:
        logging.warning("Armada is using deprecated microservice API. "
                        "Consider upgrading armada at least to version 2.5.0")
    except Exception as e:
        logging.exception(e)
    service_tags = _create_tags()
    register_service_in_armada(service_id, service_name, service_port, service_tags, container_created_timestamp,
                               single_active_instance)


def _register_services():
    num_registered = 0
    for filename in _walk_registration_files(REGISTRATION_DIRECTORY):
        _register_service_from_file(filename)
        num_registered += 1
    return num_registered


def _async_execute_local_command(command):
    p = subprocess.Popen(
        command,
        shell=True,
        preexec_fn=os.setsid,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return p


def _get_health_checks_paths(generic_path):
    paths = []
    for path in glob.glob(generic_path):
        if os.path.isfile(path):
            os.chmod(path, 0o755)
            paths.append(path)
    return paths


def _to_health_code(return_code):
    if return_code in (0, 1):
        return return_code
    return 2


def _compute_health_code(return_codes):
    if not return_codes:
        return 0
    return max(_to_health_code(x) for x in return_codes)


def _get_health_status(return_code):
    if return_code == 0:
        return 'passing'
    if return_code == 1:
        return 'warning'
    return 'critical'


def _get_consul_health_endpoint(return_code):
    if return_code == 0:
        return 'pass'
    if return_code == 1:
        return 'warn'
    return 'fail'


# service may be deregistered without our knowledge,
# if we were unsuccessful on reporting health status - that might be the case,
# so let's try to register it again and retry
@retry(num_retries=1, action=_register_services, expected_exception=ArmadaApiServiceNotFound)
def _report_health_status(microservice_id, health_check_code):
    try:
        _report_health_status_v1(microservice_id, health_check_code)
        return
    except UnsupportedArmadaApiException:
        logging.warning("Armada is using deprecated microservice API. "
                        "Consider upgrading armada at least to version 2.5.0")
    # Support for old armada (<= 2.4.3) version:
    try:
        endpoint = _get_consul_health_endpoint(health_check_code)
        response = consul_put('agent/check/{endpoint}/service:{microservice_id}'.format(**locals()))
        response.raise_for_status()
    except HTTPError:
        raise ArmadaApiServiceNotFound()


def _report_health_status_v1(microservice_id, health_check_code):
    url = '{}/v1/local/health/{}'.format(ARMADA_API_URL, microservice_id)
    r = requests.put(url, json={'health_check_code': health_check_code})
    if r.status_code == 404:
        if r.content == b'not found':
            raise UnsupportedArmadaApiException()
        service_not_found = False
        try:
            error_json = r.json()
            if error_json['error_id'] == 'SERVICE_NOT_FOUND':
                service_not_found = True
        except:
            pass
        if service_not_found:
            raise ArmadaApiServiceNotFound()
    r.raise_for_status()


def _terminate_processes(pids):
    print_err('At least one health check timed out.')
    for pid in pids:
        try:
            os.killpg(pid, signal.SIGTERM)
        except OSError:
            pass


def _run_health_checks(services_data, timeout):
    process_groups = {}
    for data in services_data:
        process_group = {}
        port = data["service_container_port"]
        for path in data["paths"]:
            command = "{path} {port}".format(**locals())
            process = _async_execute_local_command(command)
            process_group[command] = process
        if process_group:
            process_groups[data["service_id"]] = process_group
        else:
            print_err('WARNING: No health checks found.')

    pids = []
    for process_group in process_groups.values():
        pids += [p.pid for p in process_group.values()]

    timer = threading.Timer(timeout, _terminate_processes, [pids])
    timer.start()

    for process_group in process_groups.values():
        for command, process in process_group.items():
            process_stdout, process_stderr = process.communicate()
            status = _get_health_status(process.returncode)
            print_err('health-check command: {command}'.format(**locals()))
            print_err('return code: {process.returncode} ({status})'.format(**locals()))
            if process_stdout:
                print_err('stdout:\n{process_stdout}\n'.format(**locals()))
            if process_stderr:
                print_err('stderr:\n{process_stderr}\n'.format(**locals()))
            print_err()

    timer.cancel()

    health_check_code_dict = {}
    for service_id, process_group in process_groups.items():
        return_codes = [process.returncode for process in process_group.values()]
        health_check_code = _compute_health_code(return_codes)
        health_check_code_dict[service_id] = health_check_code
    return health_check_code_dict


def _get_health_checks_required_data():
    services_health_checks_data = []
    service_filenames = os.listdir(REGISTRATION_DIRECTORY)
    for service_filename in service_filenames:
        service_file_path = os.path.join(REGISTRATION_DIRECTORY, service_filename)
        with open(service_file_path) as f:
            service_health_check_data = json.load(f)

        service_health_check_generic_path = service_health_check_data.get("service_health_check_path",
                                                                          HEALTH_CHECKS_PATH_WILDCARD)
        service_health_check_data["paths"] = _get_health_checks_paths(service_health_check_generic_path)
        services_health_checks_data.append(service_health_check_data)
    return services_health_checks_data


def _service_id_to_service_name(service_id, services_data):
    for data in services_data:
        if service_id in data.values():
            return data["service_name"]


def _get_health_check_period(is_critical):
    if not is_critical:
        _get_health_check_period.critical_count = 0
        period = HEALTH_CHECKS_PERIOD + random.uniform(-HEALTH_CHECKS_PERIOD_VARIATION, HEALTH_CHECKS_PERIOD_VARIATION)
        return period

    try:
        _get_health_check_period.critical_count += 1
    except AttributeError:
        _get_health_check_period.critical_count = 1

    incrementation_period = _get_health_check_period.critical_count * HEALTH_CHECKS_PERIOD_INCREMENTATION

    return min(incrementation_period, HEALTH_CHECKS_PERIOD)


@retry(num_retries=10, action=partial(time.sleep, 0.2))
def _retry_register_services():
    """
    Wait for at least one service registration file
    """
    num_registered = _register_services()
    if not num_registered:
        raise Exception('No service registration file found.')


def main():
    _wait_for_consul()
    _retry_register_services()

    while True:
        services_data = _get_health_checks_required_data()
        start_time = time.time()
        start_datetime = datetime.now().isoformat()
        print_err('=== START: {start_datetime} ==='.format(**locals()), '\n')
        timeout = HEALTH_CHECKS_TIMEOUT
        is_critical = False

        health_check_code_dict = _run_health_checks(services_data, timeout)
        for service_id, health_check_code in health_check_code_dict.items():
            service_name = _service_id_to_service_name(service_id, services_data)
            status = _get_health_status(health_check_code)
            print_err('=== {service_name} STATUS: {status} ==='.format(**locals()))
            try:
                _report_health_status(service_id, health_check_code)
            except:
                print_exc()
            if status == 'critical':
                is_critical = True

        period = _get_health_check_period(is_critical)
        duration = time.time() - start_time
        print_err('\n', 'Health checks took {duration:.2f}s.'.format(**locals()))
        if duration < period:
            sleep_duration = period - duration
            time.sleep(sleep_duration)
        print_err()
        sys.stdout.flush()
        sys.stderr.flush()


if __name__ == '__main__':
    print('WARNING: Calling this script directly has been deprecated. Try `microservice agent` instead.',
          file=sys.stderr)
    main()
