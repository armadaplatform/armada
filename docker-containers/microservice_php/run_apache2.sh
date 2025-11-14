#!/usr/bin/env bash
set -e

# Ensure Apache runtime directory exists
mkdir -p /var/run/apache2

source /etc/apache2/envvars
exec apache2 -c "ErrorLog /dev/stdout" -DFOREGROUND
