========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-ngosolaris/badge/?style=flat
    :target: https://readthedocs.org/projects/python-ngosolaris
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/numengo/python-ngosolaris.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/numengo/python-ngosolaris

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/numengo/python-ngosolaris?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/numengo/python-ngosolaris

.. |requires| image:: https://requires.io/github/numengo/python-ngosolaris/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/numengo/python-ngosolaris/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/numengo/python-ngosolaris/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/numengo/python-ngosolaris

.. |version| image:: https://img.shields.io/pypi/v/ngosolaris.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/ngosolaris

.. |commits-since| image:: https://img.shields.io/github/commits-since/numengo/python-ngosolaris/v1.0.4.svg
    :alt: Commits since latest release
    :target: https://github.com/numengo/python-ngosolaris/compare/v1.0.4...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/ngosolaris.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/ngosolaris

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/ngosolaris.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/ngosolaris

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/ngosolaris.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/ngosolaris


.. end-badges

assistance informatique a l entraide a humaine

* Free software: GNU General Public License v3

.. skip-next

Installation
============

To install, with the command line::

    pip install ngosolaris

Settings are managed using
`simple-settings <https://github.com/drgarcia1986/simple-settings>`__
and can be overriden with configuration files (cfg, yaml, json) or with environment variables
prefixed with NGOSOLARIS_.

Documentation
=============

https://python-ngosolaris.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
