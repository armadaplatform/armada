#!/bin/bash

## alogs
##      Description:  opens mc with supervisor logs in one pane and /opt/$IMAGE_NAME dir in second
##      Usage:        alogs
##
exec mc /var/log/supervisor "/opt/${IMAGE_NAME}"
