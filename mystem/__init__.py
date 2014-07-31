# -*- coding: utf-8 -*-
"""Wraps the Mystem"""

# import fcntl
# import os
# import select
# import subprocess
# import re
# import ujson as json

from mystem import metadata


__version__ = metadata.version
__author__ = metadata.authors[0]
__license__ = metadata.license
__copyright__ = metadata.copyright


# def _set_non_blocking(fd):
#     """
#     Set the file description of the given file descriptor to non-blocking.
#     """
#     flags = fcntl.fcntl(fd, fcntl.F_GETFL)
#     flags = flags | os.O_NONBLOCK
#     fcntl.fcntl(fd, fcntl.F_SETFL, flags)


# class Mystem(object):
#     def __init__(self, mystembin=None):
#         self._mystembin = mystem
#         self._mystemargs = ["-gidc", "--format", "json"]
#         self._procin = None
#         self._procout = None
#         self._procout_no = None
#         self._proc = None

#         if self._mystembin is None:
#             self._mystembin = "/Users/negval/Downloads/mystem"

#     def _start_mystem(self):
#         self._proc = subprocess.Popen([self._mystembin] + self._mystemargs,
#                                       stdin=subprocess.PIPE,
#                                       stdout=subprocess.PIPE,
#                                       bufsize=0,
#                                       close_fds=True)

#         self._procin, self._procout = self._proc.stdin, self._proc.stdout
#         self._procout_no = self._procout.fileno()
#         _set_non_blocking(self._procout)

#     def lemmatize(self, token):
#         if self._proc is None:
#             self._start_mystem()

#         self._procin.write(token)
#         self._procin.write('\n')
#         self._procin.flush()

#         out = None
#         select.select([self._procout_no], [], [])
#         while True:
#             try:
#                 out = self._procout.readline()
#                 break
#             except IOError:
#                 rd, _, _ = select.select([self._procout_no], [], [])
#                 if self._procout_no not in rd:
#                     raise
#         obj = json.loads(out)

#         return obj

#     def _get_lemma(self, o):
#         try:
#             return o['analysis'][0]['lex'].strip()
#         except (KeyError, IndexError):
#             return o['text'].strip()

#     def tokenize(self, text):
#         text = re.sub(r"(\n|\r)", " ", text)
#         lemmas = self.lemmatize(text)
#         res = ' '.join(filter(None, map(self._get_lemma, lemmas)))
#         return res
