from __future__ import print_function

import os
import sys
import grp
import time
import stat
import json
import fcntl
import getpass
import logging
from functools import wraps
from subprocess import Popen
from datetime import timedelta
from contextlib import contextmanager

from armada_command import armada_api
from armada_command.ship_config import get_ship_config

SYNC_INTERVAL = timedelta(days=1).total_seconds()
DISPLAY_INTERVAL = timedelta(hours=1).total_seconds()
LOG_FILE_PATH = '/var/tmp/armada-version.log'
VERSION_CACHE_FILE_PATH = '/var/tmp/{}-armada-version'.format(getpass.getuser())


def _owned_file_handler(filename, mode='a', owner_group='docker'):
    gid = grp.getgrnam(owner_group).gr_gid
    if not os.path.exists(filename):
        open(filename, 'a').close()
        os.chown(filename, -1, gid)
        # -rw-rw-r--
        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
    return logging.FileHandler(filename, mode)


def get_logger(name):
    l = logging.getLogger(name)
    l.addHandler(_owned_file_handler(LOG_FILE_PATH))
    return l


logger = get_logger(__file__)


def lock_file(f, exclusive=False):
    lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    fcntl.lockf(f.fileno(), lock_type)


def unlock_file(f):
    fcntl.lockf(f.fileno(), fcntl.LOCK_UN)


def suppress_exception(logger):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except Exception:
                logger.exception('An error occurred while checking for new version of armada.')
        return wrapper
    return decorator


@contextmanager
def suppress_version_check():
    os.environ['SUPPRESS_VERSION_CHECK'] = '1'
    yield
    del os.environ['SUPPRESS_VERSION_CHECK']


@suppress_exception(logger)
def _valid_cache():
    if _cache_outdated_or_invalid():
        _sync_cache()
        return False
    return True


def _sync_cache():
    current_dir = os.path.dirname(__file__)
    with open(os.devnull) as dnull:
        Popen(['python', os.path.join(current_dir, 'sync_version.py')],
              env=dict(PYTHONPATH='/opt/armada'), stderr=dnull, stdout=dnull)


def _cache_outdated_or_invalid():
    try:
        with open(VERSION_CACHE_FILE_PATH, 'r') as f:
            lock_file(f)
            data = json.load(f)
            unlock_file(f)
    except (IOError, ValueError):
        return True

    synced_timestamp = data['synced']
    return time.time() - SYNC_INTERVAL > synced_timestamp


@suppress_exception(logger)
def _version_check():
    with open(VERSION_CACHE_FILE_PATH, 'r+') as f:
        lock_file(f, exclusive=True)
        data = json.load(f)
        displayed_timestamp = data['displayed']

        if not data['is_newer'] or time.time() - DISPLAY_INTERVAL < displayed_timestamp:
            return

        message = 'You are using armada version {}, however version {} is available. ' \
                  'You should consider upgrading armada via "bash <(curl -sL http://armada.sh/install)"' \
                  .format(armada_api.get('version'), data['latest_version'])
        print('\n' + message, file=sys.stderr)

        data['displayed'] = time.time()
        f.seek(0)
        f.truncate()
        json.dump(data, f)
        unlock_file(f)


def _check_for_updates():
    config = get_ship_config()
    try:
        return int(config.get('check_updates', 1))
    except ValueError:
        return 1

_suppress_check = 'SUPPRESS_VERSION_CHECK' in os.environ


def version_check(fun):
    @wraps(fun)
    def wrapper():
        fun()
        if not _suppress_check and _check_for_updates() and _valid_cache():
            _version_check()
    return wrapper
