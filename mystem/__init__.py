# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from . import metadata


__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright


from ._mystem import (Mystem, autoinstall)  # noqa


def main():
    autoinstall(sys.stdout)

if __name__ == '__main__':
    main()
