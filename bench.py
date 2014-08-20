#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import codecs
import timeit
import sys
import json  # noqa

import pymystem3 as mystem
import pymorphy2
import pymorphy2.tokenizers


para = """\
Внимательно, не мигая, сквозь редкие облака,
на лежащего в яслях ребенка издалека,
из глубины Вселенной, с другого ее конца,
звезда смотрела в пещеру. И это был взгляд Отца."""
para_utf8 = para.encode('utf-8')
para_unicode = para

_morph = pymorphy2.MorphAnalyzer()

_mystem = mystem.Mystem(grammar_info=False, entire_input=True)
_mystem.start()


def with_bench(func_name, profile=True):
    print 'Benchmark %s' % func_name

    if profile:
        # import ctypes
        # profiler = ctypes.CDLL("libprofiler.dylib")
        # profiler.ProfilerStart()

        # import yep
        # yep.start('%s.prof' % func_name)

        # from cStringIO import StringIO
        # import cProfile
        # import pstats
        # import sys
        # pr = cProfile.Profile()
        # pr.enable()

        pass

    rv = timeit.timeit("""%s.__call__()""" % func_name,
                       """from __main__ import %s""" % func_name,
                       number=10000)

    if profile:
        # profiler.ProfilerStop()

        # yep.stop()

        # pr.disable()
        # s = StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # sys.stderr.write(s.getvalue())

        pass

    print rv


def war_and_peace():
    for fname in ['warandpeace.txt']:
        with codecs.open(fname, 'r', 'utf-8') as f:
            # text = f.read()
            # lemmas = using_mystem(text.encode('utf-8'))
            # for t in using_mystem(text):
            #     sys.stdout.write(t)
            for line in f.xreadlines():
                for t in using_mystem(line.decode('utf-8')):
                    if isinstance(t, basestring):
                        sys.stdout.write(t)


def from_stdin():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        ts = using_mystem(line)
        # print json.dumps(ts, ensure_ascii=False)
        print 'mystem tokens=\t\t', str('').join(ts).strip()
        ts = using_pymorphy(line.decode('utf-8'))
        print 'pymorphy tokens=\t', ' '.join(ts)
        print


def using_mystem(text=para_unicode):
    # print 'text=', text
    return _mystem.lemmatize(text)


def using_pymorphy(text=para_unicode):
    tokens = pymorphy2.tokenizers.simple_word_tokenize(text)
    lemmas = list()
    for t in tokens:
        pt = _morph.parse(t)
        l = pt[0].normal_form if len(pt) >= 1 else t
        lemmas.append(l)
    return lemmas


def main():
    print("Stdin")
    from_stdin()
    # print('Война и Мир')
    # war_and_peace()
    # with_bench('using_pymorphy', profile=True)
    # print ' '.join(using_pymorphy())
    # with_bench('using_mystem', profile=True)
    # print ''.join(using_mystem())

if __name__ == '__main__':
    main()
