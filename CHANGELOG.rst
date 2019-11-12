*********
Changelog
*********

v3.0.0rc1 (2019-11-12)
======================

- Require Mopidy >= 3.0.0a4, which required the following changes:

  - Stop using removed ``Album.images`` field.

  - Use ``uris`` instead of ``uri`` when calling ``core.tracklist.add()``.

- Require Python >= 3.7. No major changes required.

- Update project setup.

v2.0.0 (2018-12-07)
===================

Major feature release.

Dependencies
------------

- Require Mopidy >= 1.1.

- Replace python-dbus with python-pydbus.

Configuration
-------------

- Remove config value ``mpris/desktop_file``. It is marked as deprecated in
  the config schema, so it will be ignored if present in the config file.

Functionality
-------------

- Ordering of playlists by playlist modification time is no longer supported.

- Update UIs when playback options change: On the Mopidy event
  ``options_changed``, emit ``PropertiesChanged`` for ``LoopStatus``,
  ``Shuffle``, ``CanGoPrevious``, and ``CanGoNext``.

- Update UIs when playback is stopped: On the Mopidy event
  ``playback_state_changed``, emit ``PropertiesChanged`` for
  ``PlaybackStatus`` and ``Metadata``. (Fixes: #23)

- Update UIs when playlists are deleted: On the Mopidy event
  ``playlist_deleted``, emit``PropertiesChanged`` for ``PlaylistCount``.

- Update track name when stream title changes:

  - The ``Metadata`` property now uses ``core.playback.get_stream_title()`` as
    ``xesam:title`` if available.

  - On the Mopidy event ``stream_title_changed``, emit ``PropertiesChanged``
    for ``Metadata``.

- Control mixer mute through the volume control:

  - The ``Volume`` property is now ``0.0`` if the mixer is muted.

  - When setting the ``Volume`` property to a positive value, the mixer is
    unmuted.

  - On the Mopidy event ``mute_changed``, emit ``PropertiesChanged`` for
    ``Volume``.

- Fallback to get cover art from ``core.library.get_images()`` if
  ``track.album.images`` is blank.

- Do not expose Mopidy's desktop file through the ``DesktopEntry`` property. If
  we set this to "mopidy", the basename of "mopidy.desktop", some MPRIS clients
  will start a new Mopidy instance in a terminal window if one clicks outside
  the buttons of the UI. This is probably never what the user wants.

Internals
---------

- Improved documentation.

- Port tests to pytest.

- Replace all usage of Mopidy APIs deprecated as of Mopidy 2.2.


v1.4.0 (2018-04-10)
===================

- Remove dependency on python-indicate and libindicate, as it is deprecated and
  it no longer seems to no be necessary to send a startup notification with
  libindicate.

- Make tests pass with Mopidy >= 2.0.

v1.3.1 (2015-08-18)
===================

- Make tests pass with Mopidy >= 1.1.

v1.3.0 (2015-08-11)
===================

- No longer allow ``Quit()`` to shut down the Mopidy server process. Mopidy has
  no public API for Mopidy extensions to shut down the server.

v1.2.0 (2015-05-05)
===================

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
===================

- Fix: Make ``OpenUri()`` work even if the tracklist is empty.

v1.1.0 (2014-01-20)
===================

- Updated extension API to match Mopidy 0.18.

v1.0.1 (2013-11-20)
===================

- Update to work with Mopidy 0.16 which changed some APIs.

- Remove redundant event loop setup already done by the ``mopidy`` process.

v1.0.0 (2013-10-08)
===================

- Moved extension out of the main Mopidy project.
