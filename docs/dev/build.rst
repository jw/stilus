Build system
============

We use poetry to build Stilus.  This ensures dependency management and
easy deployment without any hassle with setup.py, setup.cfg and Makefile.

Previously, when we are still using pipenv, life was much harder.

Below you'll find some information on the Stilus build system and on some
important build files.

pyproject.toml
--------------

The most build file is out toml file.  This is the replacement of
the regular setup.py and setup.cfg files.  It also contains the dependency
information for both the production and development environments.

In it you'll also find the configuration for Black.  Black is our code
formatter.

poetry.lock
-----------

When installing the project (via ``poetry install``) the poetry.lock file is
used to get the same version of the dependencies everywhere.  To update the
lock file you'll need to use ``poetry update``.

.pre-commit-config.yaml
-----------------------

We are using pre-commit to ensure we call black at each commit.  Pre-commit
is part of the dev dependencies.

.flake8
-------

Since we are using black, we need to ignore some flake8 guidelines.  So
``ignore = E203, E266, E501, W503`` has been added to the configuration file.

pytest
------

We are using pytest to run all our tests and to generate a coverage report.
Call this to run all the tests with coverage:

``$ poetry run pytest --cov=stilus --cov-report html --cov-report term --cov-report term-missing tests``

Continuous integration
----------------------

We are using two systems: travis and circle-ci.  One would suffice, but it is
nice to compare, no?

.travis.yml
^^^^^^^^^^^

Uses the Ubuntu Bionic Python release to install poetry on Python 3.6, 3.7
and 3.8.  Then it installs Stilus.   Runs black on it, then flake8 on the
result, then it runs pytest.

When successful, the coverage reporters are informed.

.circle-ci/config.yml
^^^^^^^^^^^^^^^^^^^^^

Uses a ocker Python release to install poetry on Python 3.6, 3.7 and 3.8.
Then it installs Stilus.   Runs black on it, then flake8 on the result,
then it runs pytest.

When successful, the coverage reporters are informed.

Coverage
--------

We use two coverage reporting tools:

codecov
^^^^^^^

`Here <https://codecov.io/gh/jw/stilus>`_ you'll find the coverage reports
from codecov.io.

coveralls
^^^^^^^^^

`Here <https://coveralls.io/github/jw/stilus>`_ you'll find the coverage
reports for coverals.io.  Looks a little nicer.
