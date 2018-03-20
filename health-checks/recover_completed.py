#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from armada_backend.recover_saved_containers import RECOVERY_COMPLETED_PATH
from armada_backend.docker_client import api

path = Path(RECOVERY_COMPLETED_PATH)


if path.exists():
    sys.exit(0)

client = api()
start_time = datetime.strptime(client.inspect_container(os.environ['HOSTNAME'])['State']['StartedAt'][:-4],
                               "%Y-%m-%dT%H:%M:%S.%f")

if (datetime.utcnow() - start_time) > timedelta(minutes=10):
    sys.exit(1)
