from __future__ import print_function

import os
import sys
import time
import json
import logging
from functools import wraps
from subprocess import Popen
from contextlib import contextmanager
from datetime import datetime, timedelta

from armada_command import armada_api
from armada_command.ship_config import get_ship_config

SYNC_INTERVAL = timedelta(days=1)
DISPLAY_INTERVAL = timedelta(hours=1)
LOCK_FILE_PATH = '/var/tmp/armada-version'
LOG_FILENAME = '/var/tmp/armada-version.log'

logging.basicConfig(filename=LOG_FILENAME)
logger = logging.getLogger(__file__)


def to_timestamp(dt_obj):
    return time.mktime(dt_obj.timetuple())


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
def _valid_lock():
    if not _lock_exists() or _lock_outdated():
        _sync_lock()
        return False
    return True


def _sync_lock():
    current_dir = os.path.dirname(__file__)
    with open(os.devnull) as dnull:
        Popen(['python', os.path.join(current_dir, 'sync_version.py')],
              env=dict(PYTHONPATH='/opt/armada'), stderr=dnull, stdout=dnull)


def _lock_exists():
    return os.path.isfile(LOCK_FILE_PATH)


def _lock_outdated():
    with open(LOCK_FILE_PATH, 'r') as f:
        data = json.load(f)

    synced_timestamp = data['synced']
    return to_timestamp(datetime.utcnow() - SYNC_INTERVAL) > synced_timestamp


@suppress_exception(logger)
def _version_check():
    with open(LOCK_FILE_PATH, 'r+') as f:
        data = json.load(f)
        displayed_timestamp = data['displayed']

        if not data['is_newer'] or to_timestamp(datetime.utcnow() - DISPLAY_INTERVAL) < displayed_timestamp:
            return

        message = 'You are using armada version {}, however version {} is available. ' \
                  'You should consider upgrading armada via "bash <(curl -sL http://armada.sh/install)"' \
                  .format(armada_api.get('version'), data['latest_version'])
        print('\n' + message, file=sys.stderr)

        data['displayed'] = to_timestamp(datetime.utcnow())
        f.truncate()
        f.seek(0)
        json.dump(data, f)


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
        if not _suppress_check and _check_for_updates() and _valid_lock():
            _version_check()
    return wrapper
