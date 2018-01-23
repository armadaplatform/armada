function ahelp {
    local DIRTOOL="/opt/microservice/scripts/tools"
    cat $DIRTOOL/* | grep -E '^##' | cut -c '3-'
}
