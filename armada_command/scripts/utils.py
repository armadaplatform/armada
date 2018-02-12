import fcntl
import grp
import logging
import os
from contextlib import contextmanager
from functools import wraps

from armada_command.scripts.update_config import LOG_FILE_PATH


def _owned_file_handler(filename, mode='a', owner_group='docker'):
    gid = grp.getgrnam(owner_group).gr_gid
    if not os.path.exists(filename):
        open(filename, 'a').close()
        os.chown(filename, -1, gid)
        os.chmod(filename, 0o664)
    return logging.FileHandler(filename, mode)


def get_logger(name):
    l = logging.getLogger(name)
    try:
        l.addHandler(_owned_file_handler(LOG_FILE_PATH))
    except IOError:
        # current user has no permissions to write to log file
        return
    else:
        return l


class SyncOpen:
    def __init__(self, filename, mode='r'):
        self.file = open(filename, mode)

    def __enter__(self):
        exclusive = self.file.mode != 'r'
        self.acquire_lock(exclusive)
        return self.file

    def __exit__(self, *args):
        self.release_lock()
        self.file.close()

    def acquire_lock(self, exclusive=False):
        lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        fcntl.lockf(self.file.fileno(), lock_type)

    def release_lock(self):
        fcntl.lockf(self.file.fileno(), fcntl.LOCK_UN)


def suppress_exception(logger):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except Exception as e:
                if logger is not None:
                    logger.exception('An error occurred while checking for new version of armada: {}.'.format(e))

        return wrapper

    return decorator


@contextmanager
def suppress_version_check():
    os.environ['SUPPRESS_VERSION_CHECK'] = '1'
    yield
    del os.environ['SUPPRESS_VERSION_CHECK']


def is_valid_response(response):
    if isinstance(response, dict):
        try:
            return response['status'] != 'error'
        except KeyError:
            pass
    return True
