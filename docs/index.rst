.. stilus documentation master file, created by
   sphinx-quickstart on Sun Oct 14 21:02:54 2018.

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

`Stilus <https://github.com/jw/stilus>`_ is the Python implementation of `Stylus <http://stylus-lang.com>`_.

Installation
------------

Install Stilus on your machine using pip:

.. code-block:: bash

 $ python -m pip install -U stilus
 $ pip install -U stilus

It might be that you'll need to install some extra dev packages. Like this:

.. code-block:: bash

 $ sudo apt install libjpeg-dev libxml2-dev libxslt1-dev

Stilus
------

.. code-block:: bash

 $ stilus --help
 Usage: stilus [OPTIONS] [INPUT] [OUTPUT]

 Options:
   -v, --verbose       Be more verbose.
   -w, --watch         Watch file(s) for changes and re-compile.
   -c, --compress      Compress CSS output.
   -p, --print         Print out the compiled CSS.
   -I, --include TEXT  Add <path> to lookup paths.
   -o, --out TEXT      Output to <dir> when passing files.
   -P, --prefix TEXT   Prefix all css classes by <prefix>.
   --hoist-atrules     Move @import and @charset to the top
   -V, --version       Display the version of Stilus.
   -h, --help          Show this message and exit.

Comparison between Stylus and Stilus
------------------------------------

Most of Stylus is implemented in Stilus, but some parts are missing:

 - Plugins
 - Caching
 - Documentation: missing an architecture document and almost all the docstrings
 - We are missing a few tests.  Currently more than 95% of the Stylus tests
   pass successfully through Stilus.
   `These <https://github.com/jw/stilus/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aopen+label%3Atest>`_
   are missing.

Below you'll find the comparison between Stylus and Stilus.

.. toctree::
   :maxdepth: 1

   The Stylus binary <diff/stilus.md>
   The Stylus test cases <diff/tests.rst>

All help is appreciated!

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
   dev/tools.md


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
this part of the documentation is for you.

.. toctree::
   :maxdepth: 1

   code/lexer_and_parser.rst
   code/nodes.rst
   code/cli.rst
   code/visitors.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
