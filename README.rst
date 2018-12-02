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

    >>> import pydbus
    >>> bus = pydbus.SessionBus()
    >>> player = bus.get('org.mpris.MediaPlayer2.mopidy')

Now you can control Mopidy through the player object. Examples:

To get properties from Mopidy, run for example::

    >>> player.PlaybackStatus
    'Playing'

To pause Mopidy's playback through D-Bus, run::

    >>> player.Pause()
    >>>

For details on the API, please refer to the `MPRIS specification
<https://specifications.freedesktop.org/mpris-spec/latest/>`__.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-mpris>`_
- `Issue tracker <https://github.com/mopidy/mopidy-mpris/issues>`_
- `Changelog <https://github.com/mopidy/mopidy-mpris/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `Stein Magnus Jodal <https://github.com/jodal>`__
- Current maintainer: `Stein Magnus Jodal <https://github.com/jodal>`__
- `Contributors <https://github.com/mopidy/mopidy-mpris/graphs/contributors>`_
