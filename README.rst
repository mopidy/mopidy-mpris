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

`Mopidy <http://www.mopidy.com/>`_ extension for controlling Mopidy through
D-Bus using the `MPRIS specification`_.

Mopidy-MPRIS supports the minimum requirements of the `MPRIS specification`_
as well as the optional `Playlists interface`_. The `TrackList interface`_
is currently not supported.

.. _MPRIS specification: https://specifications.freedesktop.org/mpris-spec/latest/
.. _Playlists interface: https://specifications.freedesktop.org/mpris-spec/latest/Playlists_Interface.html
.. _TrackList interface: https://specifications.freedesktop.org/mpris-spec/latest/Track_List_Interface.html


Installation
============

Debian/Ubuntu/Raspbian
----------------------

Install the ``mopidy-mpris`` package::

    sudo apt install mopidy-mpris

If you want the latest version of Mopidy-MPRIS, add `apt.mopidy.com`_ as an
APT archive on your system.

.. _apt.mopidy.com: https://apt.mopidy.com/

Arch Linux
----------

Install the ``mopidy-mpris`` package from `AUR`_::

    yaourt -S mopidy-mpris

.. _AUR: https://aur.archlinux.org/packages/mopidy-mpris/

Other distributions
-------------------

If Mopidy-MPRIS isn't packaged for your Linux distribution yet, install the
dependencies yourself:

- `pydbus`_ D-Bus Python bindings, which again depends on ``python-gi``. Thus
  it is usually easiest to install with your distribution's package manager.

Then install the package from `PyPI`_::

    pip install Mopidy-MPRIS

.. _pydbus: https://github.com/LEW21/pydbus
.. _PyPI: https://pypi.org/project/Mopidy-MPRIS/


Configuration
=============

No configuration is required for the MPRIS extension to work.

The following configuration values are available:

- ``mpris/enabled``: If the MPRIS extension should be enabled or not.
  Defaults to ``true``.

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


Development tips
================

Mopidy-MPRIS has an extensive test suite, so the first step for all changes
or additions is to add a test exercising the new code. However, making the
tests pass doesn't ensure that what comes out on the D-Bus bus is correct. To
introspect this through the bus, there's a couple of useful tools.


Browsing the MPRIS API with D-Feet
----------------------------------

D-Feet is a graphical D-Bus browser. On Debian/Ubuntu systems it can be
installed by running::

    apt install d-feet

Then run the ``d-feet`` command. In the D-Feet window, select the tab
corresponding to the bus you run Mopidy-MPRIS on, usually the session bus.
Then search for "MediaPlayer2" to find all available MPRIS interfaces.

To get the current value of a property, double-click it. To execute a method,
double-click it, provide any required arguments, and click "Execute".

For more information on D-Feet, see the `Gnome wiki
<https://wiki.gnome.org/Apps/DFeet>`_.


Testing the MPRIS API with pydbus
---------------------------------

To use the MPRIS API directly, start Mopidy, and then run the following in a
Python shell to use ``pydbus`` as an MPRIS client::

    >>> import pydbus
    >>> bus = pydbus.SessionBus()
    >>> player = bus.get('org.mpris.MediaPlayer2.mopidy', '/org/mpris/MediaPlayer2')

Now you can control Mopidy through the player object. To get properties from
Mopidy, run for example::

    >>> player.PlaybackStatus
    'Playing'
    >>> player.Metadata
    {'mpris:artUrl': 'https://i.scdn.co/image/8eb49b41eeb45c1cf53e1ddfea7973d9ca257777',
     'mpris:length': 342000000,
     'mpris:trackid': '/com/mopidy/track/36',
     'xesam:album': '65/Milo',
     'xesam:albumArtist': ['Kiasmos'],
     'xesam:artist': ['Rival Consoles'],
     'xesam:discNumber': 1,
     'xesam:title': 'Arp',
     'xesam:trackNumber': 5,
     'xesam:url': 'spotify:track:7CoxEEsqo3XdvUsScRV4WD'}
    >>>

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
