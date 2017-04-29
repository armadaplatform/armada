from __future__ import print_function

import os
import sys
import time
from distutils.version import StrictVersion
from functools import wraps
from subprocess import Popen

from armada_command import armada_api
from armada_command.scripts.compat import json
from armada_command.scripts.update_config import VERSION_CACHE_FILE_PATH, SYNC_INTERVAL, DISPLAY_INTERVAL
from armada_command.scripts.utils import suppress_exception, get_logger, SyncOpen, is_valid_response
from armada_command.ship_config import get_ship_config

logger = get_logger(__file__)


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
        with SyncOpen(VERSION_CACHE_FILE_PATH, 'r') as f:
            data = json.load(f)
    except (IOError, ValueError):
        return True
    synced_timestamp = data['synced']
    return time.time() - SYNC_INTERVAL > synced_timestamp


@suppress_exception(logger)
def _version_check():
    current_version = armada_api.get('version')
    if not is_valid_response(current_version):
        # skip version check since we cannot determinate current version
        return

    with SyncOpen(VERSION_CACHE_FILE_PATH, 'r+') as f:
        data = json.load(f)
        displayed_timestamp = data['displayed']

        cache_version = data['latest_version']
        current_is_newer = StrictVersion(current_version) >= StrictVersion(cache_version)
        if current_is_newer or time.time() - DISPLAY_INTERVAL < displayed_timestamp:
            return

        message = 'You are using armada version {}, however version {} is available. ' \
                  'You should consider upgrading armada via "bash <(curl -sL http://armada.sh/install)"' \
            .format(armada_api.get('version'), data['latest_version'])
        print('\n' + message, file=sys.stderr)

        data['displayed'] = time.time()
        f.seek(0)
        f.truncate()
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
        if not _suppress_check and _check_for_updates() and _valid_cache():
            _version_check()

    return wrapper
