#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
from armada_backend.recover_saved_containers import RECOVERY_COMPLETED_PATH

path = Path(RECOVERY_COMPLETED_PATH)


if path.exists():
    sys.exit(0)

uptime_seconds = time.time() - os.stat('/proc/1').st_ctime

if uptime_seconds > 10 * 60:
    sys.exit(1)
