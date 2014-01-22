************
Mopidy-MPRIS
************

.. image:: https://pypip.in/v/Mopidy-MPRIS/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-MPRIS/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-MPRIS/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-MPRIS/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/mopidy/mopidy-mpris.png?branch=master
    :target: https://travis-ci.org/mopidy/mopidy-mpris
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/mopidy/mopidy-mpris/badge.png?branch=master
   :target: https://coveralls.io/r/mopidy/mopidy-mpris?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for controlling Mopidy through the
`MPRIS D-Bus interface <http://www.mpris.org/>`_.

An example of an MPRIS client is the Ubuntu Sound Menu.


Dependencies
============

- D-Bus Python bindings. The package is named ``python-dbus`` in
  Ubuntu/Debian.

- ``libindicate`` Python bindings is needed to expose Mopidy in e.g. the
  Ubuntu Sound Menu. The package is named ``python-indicate`` in
  Ubuntu/Debian.

- An ``.desktop`` file for Mopidy installed at the path set in the
  ``mpris/desktop_file`` config value. Mopidy installs this by default.
  See usage section below for details.


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


Usage
=====

The extension is enabled by default if all dependencies are available.


Controlling Mopidy through the Ubuntu Sound Menu
------------------------------------------------

If you are running Ubuntu and installed Mopidy using the Debian package from
APT you should be able to control Mopidy through the Ubuntu Sound Menu without
any changes.

If you installed Mopidy in any other way and want to control Mopidy through the
Ubuntu Sound Menu, you must install the ``mopidy.desktop`` file which can be
found in the ``data/`` dir of the Mopidy source repo into the
``/usr/share/applications`` dir by hand::

    cd /path/to/mopidy/source
    sudo cp data/mopidy.desktop /usr/share/applications/

If the correct path to the installed ``mopidy.desktop`` file on your system
isn't ``/usr/share/applications/mopidy.conf``, you'll need to set the
``mpris/desktop_file`` config value.

After you have installed the file, start Mopidy in any way, and Mopidy should
appear in the Ubuntu Sound Menu. When you quit Mopidy, it will still be listed
in the Ubuntu Sound Menu, and may be restarted by selecting it there.

The Ubuntu Sound Menu interacts with Mopidy's MPRIS frontend. The MPRIS
frontend supports the minimum requirements of the `MPRIS specification
<http://www.mpris.org/>`_. The ``TrackList`` interface of the spec is not
supported.


Testing the MPRIS API directly
------------------------------

To use the MPRIS API directly, start Mopidy, and then run the following in a
Python shell::

    import dbus
    bus = dbus.SessionBus()
    player = bus.get_object('org.mpris.MediaPlayer2.mopidy',
        '/org/mpris/MediaPlayer2')

Now you can control Mopidy through the player object. Examples:

- To get some properties from Mopidy, run::

    props = player.GetAll('org.mpris.MediaPlayer2',
        dbus_interface='org.freedesktop.DBus.Properties')

- To quit Mopidy through D-Bus, run::

    player.Quit(dbus_interface='org.mpris.MediaPlayer2')

For details on the API, please refer to the `MPRIS specification
<http://www.mpris.org/>`__.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-mpris>`_
- `Issue tracker <https://github.com/mopidy/mopidy-mpris/issues>`_
- `Download development snapshot <https://github.com/mopidy/mopidy-mpris/tarball/master#egg=Mopidy-MPRIS-dev>`_


Changelog
=========

v1.1.1 (2014-01-22)
-------------------

- Fix: Make ``OpenUri()`` work even if the tracklist is empty.

v1.1.0 (2014-01-20)
-------------------

- Updated extension API to match Mopidy 0.18.

v1.0.1 (2013-11-20)
-------------------

- Update to work with Mopidy 0.16 which changed some APIs.

- Remove redundant event loop setup already done by the ``mopidy`` process.

v1.0.0 (2013-10-08)
-------------------

- Moved extension out of the main Mopidy project.
