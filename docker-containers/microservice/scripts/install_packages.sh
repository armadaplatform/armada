#!/bin/bash

apt-get update
apt-get upgrade -y
apt-get install -y openssh-server supervisor python python-dev curl mc software-properties-common
add-apt-repository -y ppa:vbernat/haproxy-1.5
apt-get update
apt-get install -y haproxy

# Hack for broken pip. Replace it with 'apt-get install -y python-pip' once it's fixed.
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py --no-check-certificate
python get-pip.py
ln -s /usr/local/bin/pip /usr/bin/pip

pip install -U docker-py web.py requests
