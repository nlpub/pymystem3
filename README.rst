==================================================================
 A Python wrapper of the Yandex Mystem 3.0 morphological analyzer
==================================================================

.. image:: https://travis-ci.org/Digsolab/pymystem3.png?branch=master
    :target: http://travis-ci.org/Digsolab/pymystem3
    :alt: Build Status

Introduction
============

This module contains a wrapper for an excellent morphological analyzer for Russian language `Yandex Mystem 3.0 <http://api.yandex.ru/mystem/>`_ released in June 2014.
A morphological analyzer can perform lemmatization of text and derive a set of morphological attributes for each token.
For more details about the algorithm see I. Segalovich `«A fast morphological algorithm with unknown word guessing induced by a dictionary for a web search
engine» <http://download.yandex.ru/company/iseg-las-vegas.pdf>`_, MLMTA-2003, Las Vegas, Nevada, USA.

Python is the language of choice for many computational linguists, including those working with Russian language. The main motivation for this development was absence of any Python wrapper for the Mystem, a one of the most popular morphological analyzers for Russian language along with the `PyMorphy2 <https://github.com/kmike/pymorphy2>`_, the `TreeTagger <http://corpus.leeds.ac.uk/mocky/>`_ and `AOT <http://www.aot.ru/download.php>`_.

The third version of Mystem introduces several importaint improvements, most importaintly part-of-speech disambiguation. Our wrapper runs the Mystem in the mode which performs POS disambiguation.

This wrapper is open sources under MIT license. However, please consider that the Yandex Mystem is not open source and licensed under conditions of the `Yandex License  <http://legal.yandex.ru/mystem/>`_.


System Requrements
===================

The wrapper works with CPython 2.6+/3.3+ and PyPy 1.9+.

The wrapper was tested on Ubuntu Linux 12.04+, Mac OSX 10.9+ and Windows 7+.



Installation
====================

1. Stable version: https://pypi.python.org/pypi/pymystem3. You can install it using pip::

    pip install pymystem3

.. * Documentation: http://pythonhosted.org/pymystem3


2. Latest version: https://github.com/Digsolab/pymystem3


A Quick Example
===============

::

    >>> from pymystem3 import Mystem
    >>> text = "Красивая мама красиво мыла раму"
    >>> m = Mystem()
    >>> lemmas = m.lemmatize(text)
    >>> print(''.join(lemmas))
    красивый мама красиво мыть рама


Issues
======

The current version can be considered as an alpha version, so please let us know if something does not work as expected.
Please report any bugs or requests that you have using the GitHub issue tracker (https://github.com/Digsolab/pymystem3/issues)!


Authors
=======

* Denis Sukhonin <d.sukhonin@gmail.com>, engineering
* Alexander Panchenko <panchenko.alexander@gmail.com>, conception, management
