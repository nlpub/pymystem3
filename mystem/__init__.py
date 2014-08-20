# -*- coding: utf-8 -*-

import sys

from . import metadata


__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright


from ._mystem import (Mystem, autoinstall)  # noqa
from .constants import (MYSTEM_BIN, MYSTEM_DIR, MYSTEM_EXE)


def main():
    autoinstall(sys.stdout)

if __name__ == '__main__':
    main()
