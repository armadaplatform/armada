#!/usr/bin/env bash

apt-get update
apt-get upgrade -y
apt-get install -y --no-install-recommends supervisor python python-dev python-pip curl mc less \
    software-properties-common wget gcc unzip apt-utils net-tools cron netcat sudo
add-apt-repository -y ppa:vbernat/haproxy-1.7
apt-get update
apt-get install -y --no-install-recommends haproxy
apt-get clean
rm -rf /var/lib/apt/lists/*

pip install -U pip
pip install -U setuptools
pip install -U docker-py web.py "requests==2.9.1"
