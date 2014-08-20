# -*- coding: utf-8 -*-
"""
A Python wrapper of the Yandex Mystem 3.0 morphological analyzer.
"""

from __future__ import print_function

from itertools import ifilter, imap
import os
import platform
import select
import subprocess
import sys

if sys.version_info[0] < 3:
    from cStringIO import StringIO
else:
    from io import BytesIO as StringIO

try:
    import ujson as json
except ImportError:
    import json

from .constants import (MYSTEM_BIN, MYSTEM_EXE, MYSTEM_DIR)


_TARBALL_URLS = {
    'linux': {
        '32bit': "http://download.cdn.yandex.net/mystem/mystem-3.0-linux3.5-32bit.tar.gz",
        '64bit': "http://download.cdn.yandex.net/mystem/mystem-3.0-linux3.1-64bit.tar.gz",
    },
    'darwin': "http://download.cdn.yandex.net/mystem/mystem-3.0-macosx10.8.tar.gz",
    'win': {
        '32bit': "http://download.cdn.yandex.net/mystem/mystem-3.0-win7-32bit.zip",
        '64bit': "http://download.cdn.yandex.net/mystem/mystem-3.0-win7-64bit.zip",
    },
    'freebsd': {
        '64bit': "http://download.cdn.yandex.net/mystem/mystem-3.0-freebsd9.0-64bit.tar.gz",
    }
}

_NL = unicode('\n').encode('utf-8')
_POSIX = os.name == 'posix'
_PIPELINE_MODE = _POSIX and '__pypy__' not in sys.builtin_module_names


def autoinstall(out=sys.stderr):
    """
    Install mystem binary as :py:const:`~pymystem3.constants.MYSTEM_BIN`.
    Do nothing if already installed.
    """

    if os.path.isfile(MYSTEM_BIN):
        return
    install(out)


def install(out=sys.stderr):
    """
    Install mystem binary as :py:const:`~pymystem3.constants.MYSTEM_BIN`.
    Overwrite if already installed.
    """

    import requests
    import tempfile

    url = _get_tarball_url()

    print("Installing mystem to %s from %s" % (MYSTEM_BIN, url), file=out)

    if not os.path.isdir(MYSTEM_DIR):
        os.makedirs(MYSTEM_DIR)

    tmp_fd, tmp_path = tempfile.mkstemp()
    try:
        r = requests.get(url, stream=True)
        with os.fdopen(tmp_fd, 'wb') as fd:
            for chunk in r.iter_content(64 * 1024):
                fd.write(chunk)
            fd.flush()

        if url.endswith('.tar.gz'):
            import tarfile
            with tarfile.open(tmp_path) as tar:
                tar.extract(MYSTEM_EXE, MYSTEM_DIR)
        elif url.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(tmp_path) as zip:
                zip.extractall(MYSTEM_DIR)
        else:
            raise NotImplementedError("Could not install mystem from %s" % url)
    finally:
        os.unlink(tmp_path)


def _get_on_prefix(kvs, key):
    for k, v in kvs.iteritems():
        if key.startswith(k):
            return v
    return None


def _get_tarball_url():
    bits, _ = platform.architecture()

    url = _get_on_prefix(_TARBALL_URLS, sys.platform)
    if url is None:
        raise NotImplementedError("Your system is not supported. Feel free to report bug or make a pull request.")

    if isinstance(url, basestring):
        return url

    url = url.get(bits, None)
    if url is None:
        raise NotImplementedError("Your system is not supported. Feel free to report bug or make a pull request.")

    return url


def _set_non_blocking(fd):
    """
    Set the file description of the given file descriptor to non-blocking.
    """

    if _PIPELINE_MODE:
        import fcntl
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)


class Mystem(object):

    """
    Wrap mystem binary to be able it use from Python.

    The two main methods you may use are the :py:meth:`__init__` initializer,
    and the :py:meth:`analyze` method to process your data and get mystem
    output results.

    :param  mystem_bin: path to mystem binary
    :type   mystem_bin: str
    :param  grammar_info: glue grammatical information for same lemmas in output.
    :type   grammar_info: bool
    :param  disambiguation: apply disambiguation
    :type   disambiguation: bool
    :param  entire_input: copy entire input to output
    :type   entire_input: bool

    .. note:: Default value of :py:attr:`mystem_bin` can be overwritted by :envvar:`MYSTEM_BIN`.
    """

    def __init__(self, mystem_bin=None, grammar_info=True, disambiguation=True, entire_input=True):
        self._mystem_bin = mystem_bin
        self._grammar_info = grammar_info
        self._disambiguation = disambiguation
        self._entire_input = entire_input
        self._procin = None
        self._procout = None
        self._procout_no = None
        self._proc = None

        if self._mystem_bin is None:
            self._mystem_bin = os.environ.get("MYSTEM_BIN", None)

        if self._mystem_bin is None:
            autoinstall()
            self._mystem_bin = MYSTEM_BIN

        self._mystemargs = ["--format", "json"]

        if self._grammar_info is True:
            self._mystemargs.append('-gi')

        if self._disambiguation is True:
            self._mystemargs.append('-d')

        if self._entire_input is True:
            self._mystemargs.append('-c')

    def start(self):
        """
        Run mystem binary.

        .. note:: It is not mandatory to call it. Use it if you want to avoid waiting for mystem loads.
        """

        self._start_mystem()

    def _start_mystem(self):
        self._proc = subprocess.Popen([self._mystem_bin] + self._mystemargs,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      bufsize=0,
                                      close_fds=True if _POSIX else False)

        self._procin, self._procout = self._proc.stdin, self._proc.stdout
        self._procout_no = self._procout.fileno()
        _set_non_blocking(self._procout)

    def analyze(self, text):
        """
        Make morphology analysis for a text.

        :param  text:   text to analyze
        :type   text:   str
        :returns:       result of morphology analysis.
        :rtype:         dict
        """

        result = []
        for line in text.splitlines():
            result.extend(self._analyze_impl(line))
        return result

    def lemmatize(self, text):
        """
        Make morphology analysis for a text and return list of lemmas.

        :param  text:   text to analyze
        :type   text:   str
        :returns:       list of lemmas
        :rtype:         list
        """

        need_encode = (sys.version_info[0] < 3 and isinstance(text, str))

        infos = self.analyze(text)
        lemmas = list(ifilter(None, imap(self._get_lemma, infos)))

        if need_encode is True:
            lemmas = [l.encode('utf-8') for l in lemmas]

        return lemmas

    if _PIPELINE_MODE:
        def _analyze_impl(self, text):
            if isinstance(text, unicode):
                text = text.encode('utf-8')

            if self._proc is None:
                self._start_mystem()

            self._procin.write(text)
            self._procin.write(_NL)
            self._procin.flush()

            sio = StringIO()
            obj = None
            select.select([self._procout_no], [], [])
            while True:
                try:
                    out = self._procout.read()
                    sio.write(out)
                    obj = json.loads(sio.getvalue())
                    break
                except (IOError, ValueError):
                    rd, _, _ = select.select([self._procout_no], [], [], 30)
                    if self._procout_no not in rd:
                        raise RuntimeError("Problem has been occured. Current state:\ntext:\n%s\nout:\n%s\nsio:\n%s" %
                                           (text, out, sio.getvalue()))

            return obj
    else:
        def _analyze_impl(self, text):
            if isinstance(text, unicode):
                text = text.encode('utf-8')

            if self._proc is None:
                self._start_mystem()

            self._procin.write(text)
            self._procin.write(_NL)

            out, _ = self._proc.communicate()
            self._proc = None
            try:
                obj = json.loads(out)
            except (IOError, ValueError):
                raise RuntimeError("Problem has been occured. Current state:\ntext:\n%s\nout:\n%s" %
                                   (text, out))

            return obj

    @staticmethod
    def _get_lemma(o):
        lemma = None
        try:
            lemma = o['analysis'][0]['lex']
        except (KeyError, IndexError):
            lemma = o['text'] if 'text' in o else None
        return lemma
