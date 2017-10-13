#!/usr/bin/env bash
set -ex
VERSIONS_TO_BUILD=(4 6 8)

#workdir to script directory
cd "$(dirname "${BASH_SOURCE[0]}")"

docker pull dockyard.armada.sh/microservice
docker tag dockyard.armada.sh/microservice  microservice

for NODE_VERSION in "${VERSIONS_TO_BUILD[@]}"
do
    docker build -t "microservice_node${NODE_VERSION}" --build-arg "NODE_VERSION=${NODE_VERSION}" ./
done
