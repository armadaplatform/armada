#!/usr/bin/env bash
set -e
set -x

SERVICE_NAME=microservice_packaging

#workdir to file directory
cd "$(dirname "${BASH_SOURCE[0]}")"

PACKAGE_VERSION=$1
if [[ ! -n ${PACKAGE_VERSION} ]]; then
    PACKAGE_VERSION=$(grep 'ENV MICROSERVICE_VERSION' Dockerfile | awk '{ print $3 }'  | tr -d '[[:space:]]')
fi

docker build --rm --no-cache -t "${SERVICE_NAME}" -f packaging/Dockerfile ./packaging
docker run --rm -t -v "$(pwd)/packaging:/opt/microservice" "${SERVICE_NAME}" --version="${PACKAGE_VERSION}"

mv -f "$(pwd)/packaging/armada-microservice_${PACKAGE_VERSION}_amd64.deb" "$(pwd)/"
