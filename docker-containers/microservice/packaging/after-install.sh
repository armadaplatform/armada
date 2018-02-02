#!/bin/bash

set -ex

sudo -H pip3 install -U pip setuptools
sudo -H pip2 install -U pip setuptools
sudo -H pip2 install -U web.py


mkdir -p /var/log/supervisor /var/opt/service-registration/
ln -sf /opt/microservice/microservice /opt/microservice/src

sudo -H pip2 install -U /opt/microservice
sudo -H pip3 install -U /opt/microservice

chmod +x /opt/microservice/scripts/* /opt/microservice/src/run_hooks.py

apt-get clean
rm -rf /var/lib/apt/lists/*
