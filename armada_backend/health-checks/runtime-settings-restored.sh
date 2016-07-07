#!/usr/bin/env python

from armada_command.dockyard import alias
import sys

if not alias.get_initialized():
    sys.exit(1)
