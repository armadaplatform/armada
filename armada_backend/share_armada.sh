#!/bin/bash

mkdir -p /opt/armada
cp -r /opt/armada-docker/armada_command/. /opt/armada/armada_command
cp -r /opt/armada-docker/keys/. /opt/armada/keys
chmod -R 755 /opt/armada
