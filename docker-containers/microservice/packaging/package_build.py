#!/usr/bin/python3

from argparse import ArgumentParser
import subprocess

options = {
    'depends': [
        "supervisor",
        "python",
        "python-dev",
        "python-pip",
        "python3-pip",
        "curl",
        "mc",
        "less",
        "software-properties-common",
        "wget",
        "vim",
        "gcc",
        "unzip",
        "apt-utils",
        "net-tools",
        "cron",
        "netcat",
        "sudo",
        "file",
        "iproute2",
        "bash-completion"
    ],
    'suggests': [
        "haproxy"
    ]
}


def main():
    ap = ArgumentParser()
    ap.add_argument('--version', required=True)
    args = ap.parse_args()
    version = args.version

    _create_package(options, version)


def _create_package(options, version):
    fpm_options = [
        "fpm",
        "-t", "deb",
        "-s", "dir",
        "--description", "armada",
        "-C", './microservice',
        "--license", "\"Apache 2.0\"",
        "--maintainer", "cerebro@ganymede.eu",
        "--url", "armada.sh",
        "--after-install", 'after-install.sh',
        "--name", 'armada-microservice',
        "--version", version,
        "--architecture", 'x86_64',
    ]

    for dep in options['depends']:
        fpm_options += ['--depends', dep]
    for dep in options['suggests']:
        fpm_options += ['--deb-suggests', dep]

    subprocess.check_call(fpm_options)
    print('OK')


if __name__ == '__main__':
    main()
