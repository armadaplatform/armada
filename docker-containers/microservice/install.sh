#!/bin/bash

dpkg -i  /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb
apt-get install -f -y
