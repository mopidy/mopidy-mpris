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

`Mopidy`_ extension for controlling Mopidy through D-Bus using the `MPRIS
specification`_.

Mopidy-MPRIS supports the minimum requirements of the `MPRIS specification`_
as well as the optional `Playlists interface`_. The `TrackList interface`_
is currently not supported.

.. _Mopidy: https://www.mopidy.com/
.. _MPRIS specification: https://specifications.freedesktop.org/mpris-spec/latest/
.. _Playlists interface: https://specifications.freedesktop.org/mpris-spec/latest/Playlists_Interface.html
.. _TrackList interface: https://specifications.freedesktop.org/mpris-spec/latest/Track_List_Interface.html


Table of contents
=================

- Installation_

  - `Debian/Ubuntu/Raspbian`_
  - `Arch Linux`_
  - `Other distributions`_

- Configuration_
- Usage_
- Clients_

  - `GNOME Shell builtin`_
  - `gnome-shell-extensions-mediaplayer`_
  - `gnome-shell-extensions-mpris-indicator-button`_
  - `Ubuntu Sound Menu`_

- `Advanced setups`_

  - `Running as a service`_
  - `MPRIS on the system bus`_
  - `UPnP/DLNA with Rygel`_

- `Development tips`_

  - `Browsing the MPRIS API with D-Feet`_
  - `Testing the MPRIS API with pydbus`_

- `Project resources`_
- Credits_


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

Once Mopidy-MPRIS has been installed and your Mopidy server has been
restarted, the Mopidy-MPRIS extension announces its presence on D-Bus so that
any MPRIS compatible clients on your system can interact with it. Exactly how
you control Mopidy through MPRIS depends on which MPRIS client you use.


Clients
=======

The following clients have been tested with Mopidy-MPRIS.

GNOME Shell builtin
-------------------

State:
    Not working
Tested versions:
    Ubuntu 18.10,
    GNOME Shell 3.30.1-2ubuntu1,
    Mopidy-MPRIS 2.0.0

GNOME Shell, which is the default desktop on Ubuntu 18.04 onwards, has a
builtin MPRIS client. This client seems to work well with Spotify's player,
but Mopidy-MPRIS does not show up here.

If you have any tips on what's missing to get this working, please open an
issue.

gnome-shell-extensions-mediaplayer
----------------------------------

State:
    Working
Tested versions:
    Ubuntu 18.10,
    GNOME Shell 3.30.1-2ubuntu1,
    gnome-shell-extension-mediaplayer 63,
    Mopidy-MPRIS 2.0.0
Website:
    https://github.com/JasonLG1979/gnome-shell-extensions-mediaplayer

gnome-shell-extensions-mediaplayer is a quite feature rich MPRIS client
built as an extension to GNOME Shell. With the improvements to Mopidy-MPRIS
in v2.0, this extension works very well with Mopidy.

gnome-shell-extensions-mpris-indicator-button
---------------------------------------------

State:
    Working
Tested versions:
    Ubuntu 18.10,
    GNOME Shell 3.30.1-2ubuntu1,
    gnome-shell-extensions-mpris-indicator-button 5,
    Mopidy-MPRIS 2.0.0
Website:
    https://github.com/JasonLG1979/gnome-shell-extensions-mpris-indicator-button/

gnome-shell-extensions-mpris-indicator-button is a minimalistic version of
gnome-shell-extensions-mediaplayer. It works with Mopidy-MPRIS, with the
exception of the play/pause button not changing state when Mopidy starts
playing.

If you have any tips on what's missing to get the play/pause button display
correctly, please open an issue.

Ubuntu Sound Menu
-----------------

State:
    Unknown

Historically, Ubuntu Sound Menu was the primary target for Mopidy-MPRIS'
development. Since Ubuntu 18.04 replaced Unity with GNOME Shell, this is no
longer the case. It is currently unknown to what degree Mopidy-MPRIS works
with old Ubuntu setups.

If you run an Ubuntu setup with Unity and have tested Mopidy-MPRIS, please
open an issue to share your results.


Advanced setups
===============

Running as a service
--------------------

If you have input on how to best configure Mopidy-MPRIS when Mopidy is
running as a service, please add a comment to `issue #15`_.

.. _issue #15: https://github.com/mopidy/mopidy-mpris/issues/15

MPRIS on the system bus
-----------------------

You can set the ``mpris/bus_type`` config value to ``system``. This will lead
to Mopidy-MPRIS making itself available on the system bus instead of the
logged in user's session bus.

.. note::
    Few MPRIS clients will try to access MPRIS devices on the system bus, so
    this will give you limited functionality. For example, media keys in
    GNOME Shell does not work with media players that expose their MPRIS
    interface on the system bus instead of the user's session bus.

The default setup will often not permit Mopidy to publish its service on the
D-Bus system bus, causing a warning similar to this in Mopidy's log::

    MPRIS frontend setup failed (g-dbus-error-quark:
    GDBus.Error:org.freedesktop.DBus.Error.AccessDenied: Connection ":1.3071"
    is not allowed to own the service "org.mpris.MediaPlayer2.mopidy" due to
    security policies in the configuration file (9))

To solve this, create the file
``/etc/dbus-1/system.d/org.mpris.MediaPlayer2.mopidy.conf`` with the
following contents:

.. code:: xml

    <!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
    <busconfig>
      <!-- Allow mopidy user to publish the Mopidy-MPRIS service -->
      <policy user="mopidy">
        <allow own="org.mpris.MediaPlayer2.mopidy"/>
      </policy>

      <!-- Allow anyone to invoke methods on the Mopidy-MPRIS service -->
      <policy context="default">
        <allow send_destination="org.mpris.MediaPlayer2.mopidy"/>
        <allow receive_sender="org.mpris.MediaPlayer2.mopidy"/>
      </policy>
    </busconfig>

If you run Mopidy as another user than ``mopidy``, you must
update ``user="mopidy"`` in the above file accordingly.

Once the file is in place, you must restart Mopidy for the change to take
effect.

To test the setup, you can run the following command as any user on the
system to play/pause the music::

    dbus-send --system --print-reply \
      --dest=org.mpris.MediaPlayer2.mopidy \
      /org/mpris/MediaPlayer2 \
      org.mpris.MediaPlayer2.Player.PlayPause

UPnP/DLNA with Rygel
--------------------

Rygel_ is an application that will translate between Mopidy's MPRIS interface
and UPnP. Rygel must be run on the same machine as Mopidy, but will make
Mopidy controllable by any device on the local network that can control a
UPnP/DLNA MediaRenderer.

.. _Rygel: https://wiki.gnome.org/Projects/Rygel

The setup process is approximately as follows:

1. Install Rygel.

   On Debian/Ubuntu/Raspbian::

       sudo apt install rygel

2. Enable Rygel's MPRIS plugin.

   On Debian/Ubuntu/Raspbian, edit ``/etc/rygel.conf``, find the ``[MPRIS]``
   section, and change ``enabled=false`` to ``enabled=true``.

3. Start Rygel.

   To start it as the current user::

       systemctl --user start rygel

   To make Rygel start as the current user on boot::

       systemctl --user enable rygel

4. Configure your system's firewall to allow the local network to reach
   Rygel. Exactly how is out of scope for this document.

5. Start Mopidy with Mopidy-MPRIS enabled.

6. If you view Rygel's log output with::

       journalctl --user -feu rygel

   You should see a log statement similar to::

       New plugin "org.mpris.MediaPlayer2.mopidy" available

6. If everything went well, you should now be able to control Mopidy from a
   device on your local network that can control an UPnP/DLNA MediaRenderer,
   for example the Android app BubbleUPnP.

Alternatively, `upmpdcli combined with Mopidy-MPD`_ serves the same purpose as
this setup.

.. _upmpdcli combined with Mopidy-MPD: https://docs.mopidy.com/en/latest/clients/upnp/


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

    sudo apt install d-feet

Then run the ``d-feet`` command. In the D-Feet window, select the tab
corresponding to the bus you run Mopidy-MPRIS on, usually the session bus.
Then search for "MediaPlayer2" to find all available MPRIS interfaces.

To get the current value of a property, double-click it. To execute a method,
double-click it, provide any required arguments, and click "Execute".

For more information on D-Feet, see the `GNOME wiki
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
