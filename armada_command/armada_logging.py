import os
import sys
import pwd
import grp
import logging
from logging.handlers import TimedRotatingFileHandler


ARMADA_CLI_LOG_PATH = '/var/log/armada/armada-cli.log'


def _owned_file_handler(filename, owner_group='docker'):
    gid = grp.getgrnam(owner_group).gr_gid
    if not os.path.exists(filename):
        open(filename, 'a').close()
        os.chown(filename, -1, gid)
        os.chmod(filename, 0o664)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    handler = TimedRotatingFileHandler(filename, when='midnight', backupCount=3)
    handler.setFormatter(formatter)
    return handler


def _get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    try:
        logger.addHandler(_owned_file_handler(filename))
    except IOError:
        # current user has no permissions to write to log file
        return logging.getLogger('dummy')
    return logger


def log_command():
    unix_username = pwd.getpwuid(os.getuid()).pw_name
    logger = _get_logger(unix_username, ARMADA_CLI_LOG_PATH)
    logger.info(' '.join(sys.argv[1:]))
