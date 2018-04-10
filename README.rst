************
Mopidy-MPRIS
************

.. image:: https://img.shields.io/pypi/v/Mopidy-MPRIS.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-MPRIS/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/mopidy/mopidy-mpris/master.svg?style=flat
    :target: https://travis-ci.org/mopidy/mopidy-mpris
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/mopidy/mopidy-mpris/master.svg?style=flat
   :target: https://coveralls.io/r/mopidy/mopidy-mpris
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for controlling Mopidy through the
`MPRIS D-Bus interface
<https://specifications.freedesktop.org/mpris-spec/latest/>`_.

An example of an MPRIS client is the Ubuntu Sound Menu.


Dependencies
============

- D-Bus Python bindings. The package is named ``python-dbus`` in
  Ubuntu/Debian.

- An ``.desktop`` file for Mopidy installed at the path set in the
  ``mpris/desktop_file`` config value. Mopidy installs this by default.
  See usage section below for details.


Installation
============

Debian/Ubuntu/Raspbian: Install the ``mopidy-mpris`` package from
`apt.mopidy.com <http://apt.mopidy.com/>`_::

    sudo apt-get install mopidy-mpris

Arch Linux: Install the ``mopidy-mpris`` package from
`AUR <https://aur.archlinux.org/packages/mopidy-mpris/>`_::

    yaourt -S mopidy-mpris

Else: Install the dependencies listed above yourself, and then install the
package from PyPI::

    pip install Mopidy-MPRIS


Configuration
=============

There's no configuration needed for the MPRIS extension to work.

The following configuration values are available:

- ``mpris/enabled``: If the MPRIS extension should be enabled or not.

- ``mpris/desktop_file``: Path to Mopidy's ``.desktop`` file.

- ``mpris/bus_type``: The type of D-Bus bus Mopidy-MPRIS should connect to.
  Choices include ``session`` (the default) and ``system``.


Usage
=====

The extension is enabled by default if all dependencies are available.


Running as a service and connecting to the system bus
-----------------------------------------------------

If Mopidy is running as an user without an X display, e.g. as a system service,
then Mopidy-MPRIS will fail with the default config. To fix this, you can set
the ``mpris/bus_type`` config value to ``system``. This will lead to
Mopidy-MPRIS making itself available on the system bus instead of the logged in
user's session bus. Note that few MPRIS clients will try to access MPRIS
devices on the system bus, so this will give you limited functionality.


Controlling Mopidy through the Ubuntu Sound Menu
------------------------------------------------

If you are running Ubuntu and installed Mopidy using the Debian package from
APT you should be able to control Mopidy instances running as your own user
through the Ubuntu Sound Menu without any additional setup.

If you installed Mopidy in any other way and want to control Mopidy through the
Ubuntu Sound Menu, you must install the ``mopidy.desktop`` file which can be
found in the ``data/`` dir of the Mopidy source repo into the
``/usr/share/applications`` dir by hand::

    cd /path/to/mopidy/source
    sudo cp extra/desktop/mopidy.desktop /usr/share/applications/

If the correct path to the installed ``mopidy.desktop`` file on your system
isn't ``/usr/share/applications/mopidy.desktop``, you'll need to set the
``mpris/desktop_file`` config value.

After you have installed the file, start Mopidy in any way, and Mopidy should
appear in the Ubuntu Sound Menu. When you quit Mopidy, it will still be listed
in the Ubuntu Sound Menu, and may be restarted by selecting it there.

The Ubuntu Sound Menu interacts with Mopidy's MPRIS frontend. The MPRIS
frontend supports the minimum requirements of the `MPRIS specification
<https://specifications.freedesktop.org/mpris-spec/latest/>`_. The
``TrackList`` interface of the spec is not supported.


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

- To pause Mopidy's playback through D-Bus, run::

    player.Pause(dbus_interface='org.mpris.MediaPlayer2.Player')

For details on the API, please refer to the `MPRIS specification
<https://specifications.freedesktop.org/mpris-spec/latest/>`__.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-mpris>`_
- `Issue tracker <https://github.com/mopidy/mopidy-mpris/issues>`_


Credits
=======

- Original author: `Stein Magnus Jodal <https://github.com/jodal>`__
- Current maintainer: `Stein Magnus Jodal <https://github.com/jodal>`__
- `Contributors <https://github.com/mopidy/mopidy-mpris/graphs/contributors>`_


Changelog
=========

v1.4.0 (2018-04-10)
-------------------

- Remove dependency on python-indicate and libindicate, as it is deprecated and
  it no longer seems to no be necessary to send a startup notification with
  libindicate.

- Make tests pass with Mopidy >= 2.0.

v1.3.1 (2015-08-18)
-------------------

- Make tests pass with Mopidy >= 1.1.

v1.3.0 (2015-08-11)
-------------------

- No longer allow ``Quit()`` to shut down the Mopidy server process. Mopidy has
  no public API for Mopidy extensions to shut down the server.

v1.2.0 (2015-05-05)
-------------------

- Fix crash on seek event: Update ``seeked`` event handler to accept the
  ``time_position`` keyword argument. Recent versions of Mopidy passes all
  arguments to event handlers as keyword arguments, not positional arguments.
  (Fixes: #12)

- Fix crash on tracks longer than 35 minutes: The ``mpris:length`` attribute in
  the ``Metadata`` property is now typed to a 64-bit integer.

- Update ``Seek()`` implementation to only pass positive numbers to Mopidy, as
  Mopidy 1.1 is stricter about its input validation and no longer accepts seeks
  to negative positions.

- Add a hardcoded list of MIME types to the root interface
  ``SupportedMimeTypes`` property. This is a temporary solution to be able to
  play audio through UPnP using Rygel and Mopidy-MPRIS. Long term,
  mopidy/mopidy#812 is the proper solution. (Fixes: #7, PR: #11)

- Add a ``mpris/bus_type`` config value for making Mopidy-MPRIS connect to the
  D-Bus system bus instead of the session bus. (Fixes: #9, PR: #10)

- Update tests to pass with Mopidy 1.0.

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
