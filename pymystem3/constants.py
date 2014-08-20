# -*- coding: utf-8 -*-

import os.path
import sys


_WIN = sys.platform.startswith('win')

#: Name of mystem binary
MYSTEM_EXE = "mystem.exe" if _WIN else "mystem"
#: Directory of mystem binary
MYSTEM_DIR = os.path.expanduser("~/.local/bin")
#: Full path to mystem binary
MYSTEM_BIN = os.path.join(MYSTEM_DIR, MYSTEM_EXE)
