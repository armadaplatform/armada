import time

import requests

from armada_command import armada_api
from armada_command.scripts.compat import json
from armada_command.scripts.update import VERSION_CACHE_FILE_PATH
from armada_command.scripts.utils import get_logger, SyncOpen, suppress_exception, is_valid_response

logger = get_logger(__file__)


@suppress_exception(logger)
def main():
    version = armada_api.get('version')
    if not is_valid_response(version):
        # skip sync if we cannot determine current version
        return
    r = requests.get('http://version.armada.sh/version_check', data=dict(version=version), timeout=3)
    r.raise_for_status()
    data = r.json()
    data.update({
        'displayed': 0,
        'synced': time.time(),
    })
    with SyncOpen(VERSION_CACHE_FILE_PATH, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()
