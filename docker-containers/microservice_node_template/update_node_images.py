#!/usr/bin/env python

import os
from argparse import ArgumentParser
from subprocess import check_call

VERSIONS_TO_BUILD = [ 6, 8, 10, 12, 13]


def parse_args():
    ap = ArgumentParser()
    ap.add_argument('--push', metavar='DOCKYARD')
    ap.add_argument('--squash', default=False, action='store_true')
    return ap.parse_args()


def main():
    args = parse_args()
    this_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(this_directory)
    for node_version in VERSIONS_TO_BUILD:
        image_name = 'microservice_node{}'.format(node_version)
        cmd = ['armada', 'build', '--build-arg', 'NODE_VERSION={}'.format(node_version), image_name]
        if args.squash:
            cmd.append('--squash')
        check_call(cmd)
        if args.push:
            check_call(['armada', 'push', image_name, '-d', args.push])


if __name__ == '__main__':
    main()
