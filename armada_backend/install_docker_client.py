import docker
import subprocess

version = docker.Client().version()['Version']
docker_install_command = 'curl -sSL -O https://get.docker.com/builds/Linux/x86_64/docker-{v} && chmod +x docker-{v} && sudo mv docker-{v} /usr/bin/docker'\
    .format(v=version)
subprocess.Popen(docker_install_command, stdout=subprocess.PIPE, shell=True)
