#!/bin/bash

set -e

latest_tag=$1
if [ ${latest_tag} ]; then
    tag_or_branch=${latest_tag}
else
    tag_or_branch="master"
fi

ARMADA_BASE_URL="https://raw.githubusercontent.com/armadaplatform/armada/${tag_or_branch}/"
ARMADA_REPOSITORY=dockyard.armada.sh
ARMADA_CONFIG_FILE_PATH="/etc/default/armada"

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

setup_daemon(){
    service_file=$1
    service_dest=$2
    download_file ${ARMADA_BASE_URL}install/armada-runner /tmp/armada-runner
    $sh_c "mv -f /tmp/armada-runner /usr/local/bin/armada-runner"
    $sh_c "chmod +x /usr/local/bin/armada-runner"

    download_file ${ARMADA_BASE_URL}install/$service_file /tmp/armada_service
    $sh_c "mv -f /tmp/armada_service $service_dest"
}

start_using_initd() {
    setup_daemon initd_armada /etc/init.d/armada
    $sh_c "chmod +x /etc/init.d/armada"

    if command_exists update-rc.d; then
        $sh_c "update-rc.d armada start 90 2 3 4 5 . stop 10 0 1 6 ."
    elif command_exists chkconfig; then
        $sh_c "chkconfig --level 2345 armada on"
    fi

    $sh_c "service armada restart"
}

start_using_systemd() {
    setup_daemon systemd_armada /etc/systemd/system/armada.service
    $sh_c "systemctl enable armada.service"
    $sh_c "systemctl restart armada.service"
}

+start_using_openrc() {
    setup_daemon openrc_armada /etc/init.d/armada
    $sh_c "chmod +x /etc/init.d/armada"
    $sh_c "rc-update add armada default"
}

case "$(uname -m)" in
    *64)
        ;;
    *)
        echo >&2 'Error: you are not using a 64bit platform.'
        echo >&2 'armada only supports 64bit platforms.'
        exit 1
        ;;
esac

user="$(id -un 2>/dev/null || true)"

sh_c='sh -c'
if [ "$user" != 'root' ]; then
    if command_exists sudo; then
        sh_c='sudo sh -c'
    elif command_exists su; then
        sh_c='su -c'
    else
        echo >&2 'Error: this installer needs the ability to run commands as root.'
        echo >&2 'We are unable to find either "sudo" or "su" available to make this happen.'
        exit 1
    fi
fi


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

download_file()
{
    url=$1
    local_path=$2

    $sh_c "rm -f ${local_path}"

    http_status_code='0'
    if command_exists curl; then
        http_status_code=$($sh_c "curl -sL -w \"%{http_code}\" -o ${local_path} ${url}")
    elif command_exists wget; then
        http_status_code=$($sh_c "wget -qS -O ${local_path} ${url} 2>&1 | awk '/^  HTTP/{print \$2}'")
    fi

    if [ ${http_status_code} -ne '200' ]; then
        echo >&2 "Error downloading file: ${url}"
        exit 1
    fi
}

if [ ! -d /var/log/armada ]; then
    $sh_c "mkdir /var/log/armada"
    $sh_c "chgrp docker /var/log/armada"
    $sh_c "chmod 775 /var/log/armada"
fi

#===================================================================================================

echo "Installing armada..."

COMMON_REQUIRED_PACKAGES='python'
YUM_REQUIRED_PACKAGES='conntrack-tools net-tools'
APT_REQUIRED_PACKAGES='conntrack'

POSSIBLE_PIP_COMMANDS=( 'pip2.7' 'pip-2.7' 'pip2' 'pip' )
for PIP_COMMAND in "${POSSIBLE_PIP_COMMANDS[@]}"
do
    if command_exists "${PIP_COMMAND}"; then
        pip="${PIP_COMMAND}"
        break
    fi
done

if [ -z "${pip}" ]; then
    pip='pip'
    COMMON_REQUIRED_PACKAGES="${COMMON_REQUIRED_PACKAGES} python-pip "
fi


if command_exists apt-get; then
    $sh_c "apt-get install -y ${COMMON_REQUIRED_PACKAGES} ${APT_REQUIRED_PACKAGES}"
else
    if command_exists yum; then
        $sh_c "yum install -y epel-release"
        $sh_c "yum install -y ${COMMON_REQUIRED_PACKAGES} ${YUM_REQUIRED_PACKAGES}"
    fi
fi


if ! command_exists python2.7; then
    $sh_c "echo >&2 'Required Python version 2.7'"
    exit 1
fi

$sh_c "$pip install -U 'requests>=2.9.1' 2>/dev/null"
$sh_c "$pip install -U docker-squash 2>/dev/null"

download_file ${ARMADA_BASE_URL}install/armada /tmp/armada
$sh_c "mv -f /tmp/armada /usr/local/bin/armada"
$sh_c "chmod +x /usr/local/bin/armada"

download_file ${ARMADA_BASE_URL}armada_command/armada_autocomplete /tmp/armada_autocomplete
$sh_c "mv -f /tmp/armada_autocomplete /etc/bash_completion.d/armada"
sudo bash -c ". /etc/bash_completion.d/armada"

download_file ${ARMADA_BASE_URL}armada_command/docker_utils/compatibility.py /tmp/docker_compatibility.py
trap "$sh_c 'rm -f /tmp/docker_compatibility.py'" EXIT

echo "Downloading armada image..."
$sh_c "docker pull ${ARMADA_REPOSITORY}/armada"
$sh_c "python /tmp/docker_compatibility.py tag ${ARMADA_REPOSITORY}/armada armada"
python_return_code=$?

if [ ${python_return_code} != 0 ]; then
    exit 1
fi

# Make sure that config file exists
touch ARMADA_CONFIG_FILE_PATH

if command_exists systemctl; then
    start_using_systemd
elif command_exists update-rc.d || command_exists chkconfig; then
    start_using_initd
elif command_exists rc-status; then
    start_using_openrc
else
    echo "No initd or systemd installed."
    exit 1
fi

hash -r

#===================================================================================================
