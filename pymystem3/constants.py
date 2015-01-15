# -*- coding: utf-8 -*-

import os
import os.path
import sys


def _find_mystem(exe):
    fpath = os.getenv("MYSTEM3_PATH", None)
    if fpath and os.path.isfile(fpath) and os.access(fpath, os.X_OK):
        return os.path.dirname(fpath), fpath

    for dir in os.getenv("PATH", "").split(os.pathsep):
        fpath = os.path.join(dir, exe)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return dir, fpath

    dir = os.path.expanduser("~/.local/bin")
    fpath = os.path.join(dir, exe)

    return dir, fpath


_WIN = sys.platform.startswith('win')

#: Name of mystem binary
MYSTEM_EXE = "mystem.exe" if _WIN else "mystem"

_mystem_info = _find_mystem(MYSTEM_EXE)

#: Directory of mystem binary
MYSTEM_DIR = _mystem_info[0]
#: Full path to mystem binary
MYSTEM_BIN = _mystem_info[1]
