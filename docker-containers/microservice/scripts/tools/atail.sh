#!/bin/bash

# Command:      atail
# Description:  runs [tail -f] for /var/log/supervisor files
# Usage:        atail [FILENAME]
exec tail -f "/var/log/supervisor/${1}"*
