import getpass
from datetime import timedelta

SYNC_INTERVAL = timedelta(days=1).total_seconds()
DISPLAY_INTERVAL = timedelta(hours=1).total_seconds()
LOG_FILE_PATH = '/var/tmp/armada-version.log'
VERSION_CACHE_FILE_PATH = '/var/tmp/{}-armada-version'.format(getpass.getuser())
