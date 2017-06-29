#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import subprocess
from glob import glob


HOOKS = []
HOOKS_PATH_WILDCARD = '/opt/*/hooks'


def register_hook(name):
        global HOOKS
        if name in HOOKS:
            raise Exception('Hook {} already registered!'.format(name))
        HOOKS.append(name)


def _get_hook_files(hook_name):
    global HOOKS_PATH_WILDCARD
    files = os.path.join(HOOKS_PATH_WILDCARD, hook_name, '*')
    for hook_file_path in sorted(glob(files)):
        if not os.path.isdir(hook_file_path):
            yield hook_file_path


def _run_hook(path):
    os.chmod(path, 0o755)
    os.system('sync')
    print('Executing hook: {}'.format(path))
    try:
        subprocess.check_call([path])
    except (OSError, subprocess.CalledProcessError) as e:
        print('Error: {}'.format(e))
    finally:
        print()


def run(hook_name):
    global HOOKS
    if hook_name not in HOOKS:
        raise Exception('There is no registered hook called {}'
                        .format(hook_name))

    for f in _get_hook_files(hook_name):
        _run_hook(f)


register_hook('pre-stop')


if __name__ == "__main__":
    assert len(sys.argv) == 2
    run(sys.argv[1])

