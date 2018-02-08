#!/bin/bash

set -ex

sudo -H pip3 install -U pip setuptools
sudo -H pip2 install -U pip setuptools
sudo -H pip2 install -U web.py

mkdir -p /var/log/supervisor /var/opt/service-registration/
ln -sf /opt/microservice/microservice /opt/microservice/src

echo VERSION = \"<%= version %>\" > /opt/microservice/microservice/version.py

sudo -H pip2 install -U /opt/microservice
sudo -H pip3 install -U /opt/microservice

chmod +x /opt/microservice/scripts/* /opt/microservice/src/run_hooks.py

grep 'source /opt/microservice/scripts/tools/microservice_bashrc.source' /etc/bash.bashrc || {
    echo "source /opt/microservice/scripts/tools/microservice_bashrc.source" >> /etc/bash.bashrc
}
