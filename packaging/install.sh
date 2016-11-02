#!/bin/bash
set -e

ARMADA_REPOSITORY='dockyard.armada.sh'
. '/opt/armada/version'

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

start_using_initd() {
    if command_exists update-rc.d; then
        $sh_c "update-rc.d armada start 90 2 3 4 5 . stop 10 0 1 6 ."
    elif command_exists chkconfig; then
        $sh_c "chkconfig --level 2345 armada on"
    fi

    $sh_c "service armada restart"
}

start_using_systemd() {
    $sh_c "rm /etc/init.d/armada"
    $sh_c "systemctl daemon-reload"
    $sh_c "systemctl enable armada.service"
    $sh_c "systemctl restart armada.service"
}

sh_c='sh -c'

if ! command_exists docker; then
    echo >&2 '"armada" requires docker to be installed first. Try installing it with:'
    echo >&2 '    curl -sL https://get.docker.com/ | sh'
    exit 1
fi

set +e
$sh_c "docker info > /dev/null 2>&1"
if [ $? != 0 ]; then
    echo >&2 "Cannot run 'docker' command. Is docker running? Try 'docker -d'."
    exit 1
fi
set -e

if [ ! -d /var/log/armada ]; then
    $sh_c "mkdir /var/log/armada"
    $sh_c "chgrp docker /var/log/armada"
    $sh_c "chmod 775 /var/log/armada"
fi


POSSIBLE_PIP_COMMANDS=( 'pip2.7' 'pip-2.7' 'pip2' 'pip' )
for PIP_COMMAND in "${POSSIBLE_PIP_COMMANDS[@]}"
do
    if command_exists "${PIP_COMMAND}"; then
        pip="${PIP_COMMAND}"
        break
    fi
done


$sh_c "$pip install -U 'requests>=2.9.1' docker-squash 2>/dev/null"

sudo bash -c ". /etc/bash_completion.d/armada"

echo "Downloading armada image..."
$sh_c "docker pull ${ARMADA_REPOSITORY}/armada:${ARMADA_VERSION}"
$sh_c "python /opt/armada/docker_compatibility.py tag ${ARMADA_REPOSITORY}/armada:${ARMADA_VERSION} armada:${ARMADA_VERSION}"

if command_exists systemctl; then
    start_using_systemd
elif command_exists update-rc.d || command_exists chkconfig; then
    start_using_initd
else
    echo "No initd or systemd installed."
    exit 1
fi

hash -r
