#!/bin/bash

## acd
##      Description:  changes cwd to /opt/$IMAGE_NAME/[DIRECTORY]
##      Usage:        acd [DIRECTORY]
##
function acd {
    cd /opt/${IMAGE_NAME}/${1}
}

## actl
##      Description:  alias for supervisorctl
##      Usage:        actl [ACTION] [SERVICE]
##
alias actl="supervisorctl"


function ahelp {
    local DIRTOOL="/opt/microservice/scripts/tools"
    cat $DIRTOOL/* | grep -E '^##' | cut -c '3-'
}


source /etc/bash_completion