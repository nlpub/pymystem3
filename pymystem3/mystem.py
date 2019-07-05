# -*- coding: utf-8 -*-
"""
A Python wrapper of the Yandex Mystem 3.1 morphological analyzer.
"""

from __future__ import print_function

from itertools import ifilter, imap
import os
import platform
import select
import subprocess
import sys
import socket

if sys.version_info[0] < 3:
    from cStringIO import StringIO
else:
    from io import BytesIO as StringIO

try:
    import ujson as json
except ImportError:
    import json

from .constants import (MYSTEM_BIN, MYSTEM_EXE, MYSTEM_DIR)

try:
    broken_pipe = BrokenPipeError
except NameError:
    broken_pipe = socket.error


_TARBALL_URLS = {
    'linux': {
        '64bit': "http://download.cdn.yandex.net/mystem/mystem-3.1-linux-64bit.tar.gz",
    },
    'darwin': "http://download.cdn.yandex.net/mystem/mystem-3.1-macosx.tar.gz",
    'win': {
        '64bit': "http://download.cdn.yandex.net/mystem/mystem-3.1-win-64bit.zip",
    },
}

_NL = unicode('\n').encode('utf-8')
_POSIX = os.name == 'posix'


_PIPELINE_MODE = False
if _POSIX and '__pypy__' in sys.builtin_module_names:
    _PIPELINE_MODE = sys.pypy_version_info >= (2, 5, 0)
elif _POSIX:
    _PIPELINE_MODE = True


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
            tar = tarfile.open(tmp_path)
            try:
                tar.extract(MYSTEM_EXE, MYSTEM_DIR)
            finally:
                tar.close()
        elif url.endswith('.zip'):
            import zipfile
            zip = zipfile.ZipFile(tmp_path)
            try:
                zip.extractall(MYSTEM_DIR)
            finally:
                zip.close()
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
    :param  weight: print context-independent lemma weight
    :type   weight: bool
    :param  generate_all: generate all possible hypotheses
    :type   generate_all: bool
    :param  fixlist: path to a custom dictionary to use for analysis
    :type   fixlist: str
    :param  use_english_names: english names of grammemes
    :type   use_english_names: bool

    .. note:: Default value of :py:attr:`mystem_bin` can be overwritted by :envvar:`MYSTEM_BIN`.
    """

    def __init__(
        self,
        mystem_bin=None,
        grammar_info=True,
        disambiguation=True,
        entire_input=True,
        weight=True,
        generate_all=False,
        fixlist=None,
        use_english_names=False
    ):
        self._mystem_bin = mystem_bin
        self._grammar_info = grammar_info
        self._disambiguation = disambiguation
        self._entire_input = entire_input
        self._weight = weight
        self._generate_all = generate_all
        self._fixlist = fixlist
        self._use_english_names = use_english_names
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

        if self._weight is True:
            self._mystemargs.append('--weight')

        if self._generate_all is True:
            self._mystemargs.append('--generate-all')

        if self._fixlist is not None:
            self._mystemargs.append('--fixlist')
            self._mystemargs.append(self._fixlist)
            
        if self._use_english_names is True:
            self._mystemargs.append('--eng-gr')

    def __del__(self):
        self.close()  # terminate process on exit

    def __enter__(self):
        if self._proc is None:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        """
        Run mystem binary.

        .. note:: It is not mandatory to call it. Use it if you want to avoid waiting for mystem loads.
        """

        self._start_mystem()

    def close(self):
        if self._proc is not None:
            self._proc.terminate()  # Send TERM signal to process
            self._procin.close()  # Then close stdin
            self._procout.close()  # And stdout
            self._proc.wait()  # Finally wait for terminaion

        self._procin = None
        self._procout = None
        self._procout_no = None
        self._proc = None

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
            try:
                result.extend(self._analyze_impl(line))
            except broken_pipe:
                self.close()
                self.start()
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
            out = None
            obj = None
            select.select([self._procout_no], [], [])
            while True:
                try:
                    out = self._procout.read()
                    sio.write(out)
                    obj = json.loads(sio.getvalue().decode('utf-8'))
                    break
                except (IOError, ValueError):
                    rd, _, _ = select.select([self._procout_no], [], [], 30)
                    if self._procout_no not in rd:
                        raise RuntimeError("Problem has been occured. Current state:\ntext:\n%r\nout:\n%r\nsio:\n%r" %
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
                #obj = json.loads(out)
                obj = json.loads(out.decode('utf-8'))
            except (IOError, ValueError):
                raise RuntimeError("Problem has been occured. Current state:\ntext:\n%r\nout:\n%r" %
                                   (text, out))

            return obj

    @staticmethod
    def _get_lemma(o):
        try:
            return o['analysis'][0]['lex']
        except (KeyError, IndexError):
            return o['text'] if 'text' in o else None
