from __future__ import print_function
import datetime
import glob
import os
import random
import subprocess
import time
import signal
import sys
import threading
import traceback
import json

import requests

from register_in_service_discovery import REGISTRATION_DIRECTORY
from common.consul import consul_get

HEALTH_CHECKS_PATH_WILDCARD = '/opt/*/health-checks/*'
HEALTH_CHECKS_TIMEOUT = 10
HEALTH_CHECKS_PERIOD_VARIATION = 2
HEALTH_CHECKS_PERIOD_INCREMENTATION = 2
INITIAL_HEALTH_CODE = 0  # passing


def print_err(*objs):
    print(*objs, file=sys.stderr)


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


def _mark_health_status(service_id, health_check_code):
    endpoint = _get_consul_health_endpoint(health_check_code)
    assert consul_get('agent/check/{endpoint}/service:{service_id}'.format(**locals())).status_code == requests.codes.ok


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


def main():
    # We give register_in_service_discovery.py script time to register services before first check.
    time.sleep(1)
    since_last_pass = 0

    while True:
        services_data = _get_health_checks_required_data()
        start_time = time.time()
        start_datetime = datetime.datetime.now().isoformat()
        print_err('=== START: {start_datetime} ==='.format(**locals()))
        timeout = HEALTH_CHECKS_TIMEOUT
        period = timeout + random.uniform(-HEALTH_CHECKS_PERIOD_VARIATION, HEALTH_CHECKS_PERIOD_VARIATION)
        is_critical = False

        print_err('\n')
        health_check_code_dict = _run_health_checks(services_data, timeout)
        for service_id, health_check_code in health_check_code_dict.items():
            service_name = _service_id_to_service_name(service_id, services_data)
            status = _get_health_status(health_check_code)
            print_err('=== {service_name} STATUS: {status} ==='.format(**locals()))
            try:
                _mark_health_status(service_id, health_check_code)
            except:
                traceback.print_exc()
            if status == 'critical':
                is_critical = True

        if is_critical:
            since_last_pass += 1
            if since_last_pass * HEALTH_CHECKS_PERIOD_INCREMENTATION < timeout:
                period = since_last_pass * HEALTH_CHECKS_PERIOD_INCREMENTATION
        else:
            since_last_pass = 0

        duration = time.time() - start_time
        print_err('Health checks took {duration:.2f}s.'.format(**locals()))
        if duration < period:
            sleep_duration = period - duration
            time.sleep(sleep_duration)
        print_err()


if __name__ == '__main__':
    main()
