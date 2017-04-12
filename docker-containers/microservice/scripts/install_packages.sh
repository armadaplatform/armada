#!/usr/bin/env bash

apt-get update
apt-get upgrade -y
apt-get install -y supervisor python python-dev python-pip curl mc software-properties-common wget gcc unzip --no-install-recommends
add-apt-repository -y ppa:vbernat/haproxy-1.6
apt-get update
apt-get install -y haproxy --no-install-recommends
apt-get clean
rm -rf /var/lib/apt/lists/*

pip install -U pip
pip install -U setuptools
pip install -U docker-py web.py "requests==2.9.1"
