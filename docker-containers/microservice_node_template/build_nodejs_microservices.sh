#!/usr/bin/env bash
set -ex
VERSIONS_TO_BUILD=(4 6 8)

#workdir to script directory
cd "$(dirname "${BASH_SOURCE[0]}")"

for NODE_VERSION in "${VERSIONS_TO_BUILD[@]}"
do
    armada build --build-arg "NODE_VERSION=${NODE_VERSION}" "microservice_node${NODE_VERSION}"
done
