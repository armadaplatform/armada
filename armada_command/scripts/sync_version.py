import json
import time

import requests

from armada_command import armada_api
from armada_command.scripts.update import VERSION_CACHE_FILE_PATH, suppress_exception, lock_file,\
    unlock_file, get_logger


logger = get_logger(__name__)


@suppress_exception(logger)
def main():
    r = requests.get('http://192.168.2.245:4999/version_check/', data=dict(version=armada_api.get('version')))
    r.raise_for_status()
    data = r.json()
    data.update({
        'displayed': 0,
        'synced': time.time(),
    })
    with open(VERSION_CACHE_FILE_PATH, 'w') as f:
        lock_file(f, exclusive=True)
        json.dump(data, f)
        unlock_file(f)

if __name__ == '__main__':
    main()
