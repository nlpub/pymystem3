==================================================================
 A Python wrapper of the Yandex Mystem 3.0 morphological analyzer
==================================================================

Introduction
============

TBD


How to get pymystem3
====================

#. GitHub (code repository, issues): https://github.com/Digsolab/pymystem3

#. PyPI (installable, stable distributions): https://pypi.python.org/pypi/pymystem3. You can install it using pip::

       pip install pymystem3

.. * Documentation: http://injector.readthedocs.org

pymystem3 works with CPython 2.6+/3.3+ and PyPy 1.9+.


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

Please report any bugs or requests that you have using the GitHub issue tracker!


Authors
=======

* Denis Sukhonin <d.sukhonin@gmail.com>
