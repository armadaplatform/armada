#!/bin/bash

mkdir -p /var/run/sshd

adduser docker --disabled-password
echo "docker ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/docker
chmod 4755 /usr/bin/sudo

mkdir -p /home/docker/.ssh
cp /opt/microservice/ssh/authorized_keys /home/docker/.ssh/authorized_keys
chown docker:docker -R /home/docker

sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
sed -ri 's/#UsePAM no/UsePAM no/g' /etc/ssh/sshd_config
