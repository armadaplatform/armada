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

docker build --rm -t "${SERVICE_NAME}" -f Dockerfile ./
docker run --rm -t -v "$(pwd)/../:/opt/armada" "${SERVICE_NAME}" --version="${PACKAGE_VERSION}"
