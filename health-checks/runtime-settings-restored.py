#!/usr/bin/env python3

from armada_command.dockyard import alias
import sys

if not alias.get_initialized():
    sys.exit(1)
