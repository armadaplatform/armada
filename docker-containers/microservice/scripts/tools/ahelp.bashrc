function ahelp {
    local DIRTOOL="/opt/microservice/scripts/tools"
    cat $DIRTOOL/* | grep '##' | grep -v 'AVOID_THIS_##' | cut -c '3-'
}
