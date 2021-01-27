#!/usr/bin/env bash

set -e

VENV_PATH=/tmp/armada-command
if [[ ! -d "${VENV_PATH}" ]]; then
	virtualenv -p $(type -p python3) "${VENV_PATH}"
fi
source "${VENV_PATH}"/bin/activate
python3 -m pip install -r armada_command/armada_command_requirements.txt
python3 -m tests.unit_tests UnitTests.test_import_of_all_command_python_files
deactivate

VENV_PATH=/tmp/armada-backend
if [[ ! -d "${VENV_PATH}" ]]; then
	virtualenv -p $(type -p python3) "${VENV_PATH}"
fi
source "${VENV_PATH}"/bin/activate
python3 -m pip install docker-containers/microservice/packaging/microservice/opt/microservice
python3 -m pip install -r armada_backend/armada_backend_requirements.txt
python3 -m tests.unit_tests UnitTests.test_import_of_all_backend_python_files
deactivate
