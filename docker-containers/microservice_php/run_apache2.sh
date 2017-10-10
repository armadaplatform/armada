#!/usr/bin/env bash
set -e

source /etc/apache2/envvars
$(command -v apache2)  -c "ErrorLog /dev/stdout" -DFOREGROUND
