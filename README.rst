************
Mopidy-MPRIS
************

.. image:: https://pypip.in/v/Mopidy-MPRIS/badge.png
    :target: https://crate.io/packages/Mopidy-MPRIS/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-MPRIS/badge.png
    :target: https://crate.io/packages/Mopidy-MPRIS/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/mopidy/mopidy-mpris.png?branch=master
    :target: https://travis-ci.org/mopidy/mopidy-mpris
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/mopidy/mopidy-mpris/badge.png?branch=master
   :target: https://coveralls.io/r/mopidy/mopidy-mpris?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for controlling Mopidy through the
`MPRIS D-Bus interface <http://www.mpris.org/>`_.


Installation
============

Install by running::

    pip install Mopidy-MPRIS

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

There's no configuration needed for the MPRIS extension to work.

The following configuration values are available:

- ``mpris/enabled``: If the MPRIS extension should be enabled or not.
- ``mpris/desktop_file``: Path to Mopidy's ``.desktop`` file.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-mpris>`_
- `Issue tracker <https://github.com/mopidy/mopidy-mpris/issues>`_
- `Download development snapshot <https://github.com/mopidy/mopidy-mpris/tarball/master#egg=Mopidy-MPRIS-dev>`_


Changelog
=========

v0.1.0 (UNRELEASED)
-------------------

- Moved extension out of the main Mopidy project.
