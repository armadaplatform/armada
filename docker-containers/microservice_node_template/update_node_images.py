#!/usr/bin/env python

import os
from argparse import ArgumentParser
from subprocess import check_call

VERSIONS_TO_BUILD = [14, 16]


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('--push', metavar='DOCKYARD')
    ap.add_argument('--squash', default=False, action='store_true')
    return ap.parse_args()


def main():
    args = parse_args()
    this_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(this_directory)

    dockerfiles = [filename for filename in os.listdir(this_directory)
        if os.path.isfile(filename) and filename.startswith('Dockerfile')]

    for dockerfile in dockerfiles:
        dockerfile_postfix = dockerfile.replace('Dockerfile', '')
        for node_version in VERSIONS_TO_BUILD:
            image_name = 'microservice_node{}{}'.format(node_version, dockerfile_postfix)
            cmd = ['armada', 'build', '--file', dockerfile, '--build-arg', 'NODE_VERSION={}'.format(node_version), image_name]

            if args.squash:
                cmd.append('--squash')

            check_call(cmd)

            if args.push:
                cmd = ['armada', 'push', image_name, '-d', args.push]
                check_call(cmd)


if __name__ == '__main__':
    main()
