#!/usr/bin/env bash
set -e
set -x

SERVICE_NAME=armada_builder

#workdir to file directory
cd "$(dirname "${BASH_SOURCE[0]}")"

PACKAGE_VERSION=$1
if [[ ! -n ${PACKAGE_VERSION} ]]; then
    PACKAGE_VERSION=$(grep 'ENV ARMADA_VERSION' ../Dockerfile | awk '{ print $3 }'  | tr -d '[[:space:]]')
fi


stop_builder_containers()
{
    #disable previous trap
    trap - EXIT HUP INT QUIT PIPE TERM
    armada stop -a "${SERVICE_NAME}"
}

trap stop_builder_containers EXIT HUP INT QUIT PIPE TERM

armada build ${SERVICE_NAME}

chmod +x build.py
CONTAINER_ID=$(armada run "${SERVICE_NAME}" -v "$(pwd)/../:/opt/armada" -d local | grep -oh 'Service is running in container [[:alnum:]]*' | awk '{print $NF}')
sleep 5

armada ssh "$CONTAINER_ID" python3 packaging/build.py --version="${PACKAGE_VERSION}"
