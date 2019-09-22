.. stilus documentation master file, created by
   sphinx-quickstart on Sun Oct 14 21:02:54 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stilus: Stylus in Python
========================

Release |version|.

.. image:: https://img.shields.io/travis/jw/stilus/master.svg?style=flat-square
    :target: https://travis-ci.org/jw/stilus

.. image:: https://img.shields.io/codecov/c/github/jw/stilus/master.svg?style=flat-square
    :target: https://codecov.io/gh/jw/stilus

.. image:: https://img.shields.io/pypi/dm/stilus.svg?style=flat-square
    :target: https://pypi.org/project/stilus/#files

.. image:: https://img.shields.io/pypi/v/stilus.svg?style=flat-square
    :target: https://pypi.org/project/stilus/#history

.. image:: https://img.shields.io/pypi/pyversions/stilus.svg?style=flat-square
    :target: https://pypi.org/project/stilus/#description

.. image:: https://img.shields.io/pypi/l/stilus?style=flat-square
    :target: https://pypi.org/project/stilus/

**Stilus** is the Python implementation of `Stylus <http://stylus-lang.com>`_.

.. note:: **Stilus** is not ready yet, but is nearing completion! Almost all built-in functions are implemented; 6 of the 60+ are missing. Most things work, but there is far too little documentation. More tests are required an the Stilus bin is incomplete.  **So all help is appreciated!**

The Plan
--------

The ongoing work, the future plans and the work done.

.. toctree::
   :maxdepth: 1

   plan/current.md
   plan/future.md
   plan/history.md

Developing Stilus
-----------------

The development of Stilus, some todo's and thoughts.

.. toctree::
   :maxdepth: 1

   dev/architecture.md
   dev/thoughts.md
   dev/codeguidelines.md
   dev/migration.md
   dev/workflow.md

Issues
------

Some built-in functions do not work properly yet; arrays/lists of blocks are
handled weirdly.

.. toctree::
   :maxdepth: 1

   bifs.md
   blocks.rst


Code
----

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.  (c) requests ;-)

.. toctree::
   :maxdepth: 1

   code.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
