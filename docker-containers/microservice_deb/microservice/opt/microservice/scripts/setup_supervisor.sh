#!/usr/bin/env bash

mkdir -p /var/log/supervisor
cp /opt/microservice/supervisor/* /etc/supervisor/conf.d/
