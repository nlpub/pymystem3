# -*- coding: utf-8 -*-

import os.path
import sys


_WIN = sys.platform.startswith('win')

MYSTEM_EXE = "mystem.exe" if _WIN else "mystem"
MYSTEM_DIR = os.path.expanduser("~/.local/bin")
MYSTEM_BIN = os.path.join(MYSTEM_DIR, MYSTEM_EXE)
