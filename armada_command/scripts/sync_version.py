import json
import logging
from datetime import datetime

import requests

from armada_command import armada_api
from armada_command.scripts.update import LOCK_FILE_PATH, suppress_exception, to_timestamp


logger = logging.getLogger(__file__)


@suppress_exception(logger)
def main():
    r = requests.get('http://192.168.2.245:4999/version_check/', data=dict(version=armada_api.get('version')))
    r.raise_for_status()
    data = r.json()
    data.update({
        'displayed': 0,
        'synced': to_timestamp(datetime.utcnow()),
    })
    with open(LOCK_FILE_PATH, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()
