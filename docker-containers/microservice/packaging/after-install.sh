#!/bin/bash

set -ex

sudo -H python3 -m pip install --upgrade 'pip<21.0'
sudo -H python3 -m pip install --upgrade 'setuptools<51.0.0'
sudo -H python3 -m pip install --upgrade web.py

mkdir -p /var/log/supervisor /var/opt/service-registration/
ln -sf /opt/microservice/microservice /opt/microservice/src

echo VERSION = \"<%= version %>\" > /opt/microservice/microservice/version.py

sudo -H python3 -m pip install --upgrade /opt/microservice

chmod +x /opt/microservice/scripts/* /opt/microservice/src/run_hooks.py

grep 'source /opt/microservice/scripts/tools/microservice_bashrc.source' /etc/bash.bashrc || {
    echo "source /opt/microservice/scripts/tools/microservice_bashrc.source" >> /etc/bash.bashrc
}
