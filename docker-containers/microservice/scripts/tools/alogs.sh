#!/bin/bash

# Command:      alogs
# Description:  opens mc with supervisor logs in one pane and /opt/$IMAGE_NAME dir in second
exec mc /var/log/supervisor "/opt/${IMAGE_NAME}"
