# -*- coding: utf-8 -*-

from __future__ import print_function

import fileinput
import json
import sys

from .mystem import (MYSTEM_BIN, Mystem, autoinstall)


def main(args=None):
    autoinstall(sys.stderr)

    print("mystem is placed in %s" % MYSTEM_BIN, file=sys.stderr)

    if sys.stdin.isatty():
        return

    mystem = Mystem()
    for line in fileinput.input():
        info = mystem.analyze(line.strip())
        print(json.dumps(info, ensure_ascii=False, indent=4), file=sys.stdout)

if __name__ == '__main__':
    main()
