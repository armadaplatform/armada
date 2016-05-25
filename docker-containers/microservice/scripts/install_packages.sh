#!/usr/bin/env bash

apt-get update
apt-get upgrade -y
apt-get install -y supervisor python python-dev python-pip curl mc software-properties-common wget
add-apt-repository -y ppa:vbernat/haproxy-1.6
apt-get update
apt-get install -y haproxy

pip install -U pip
pip install -U docker-py web.py "requests==2.9.1"
