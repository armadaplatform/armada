#!/usr/bin/env bash

apt-get update
apt-get upgrade -y
apt-get install -y --no-install-recommends supervisor python python-dev python-pip curl mc less \
    software-properties-common wget vim gcc unzip apt-utils net-tools cron netcat sudo file iproute2 bash-completion
add-apt-repository -y ppa:vbernat/haproxy-1.7
apt-get update
apt-get install -y --no-install-recommends haproxy
apt-get clean
rm -rf /var/lib/apt/lists/*

pip install -U pip
pip install -U setuptools
pip install -U "docker==2.4.2" web.py "requests==2.9.1"
