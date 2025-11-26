# mopidy-mpris

[![Latest PyPI version](https://img.shields.io/pypi/v/mopidy-mpris)](https://pypi.org/p/mopidy-mpris)
[![CI build status](https://img.shields.io/github/actions/workflow/status/mopidy/mopidy-mpris/ci.yml)](https://github.com/mopidy/mopidy-mpris/actions/workflows/ci.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/mopidy/mopidy-mpris)](https://codecov.io/gh/mopidy/mopidy-mpris)

[Mopidy](https://mopidy.com/) extension for controlling Mopidy through the MPRIS
D-Bus interface.

Mopidy-MPRIS supports the minimum requirements of the [MPRIS specification][1]
as well as the optional [Playlists interface][2]. The [TrackList interface][3]
is currently not supported.

[1]: https://specifications.freedesktop.org/mpris-spec/latest/
[2]: https://specifications.freedesktop.org/mpris-spec/latest/Playlists_Interface.html
[3]: https://specifications.freedesktop.org/mpris-spec/latest/Track_List_Interface.html


## Maintainer wanted

Mopidy-MPRIS is currently kept on life support by the Mopidy core developers.
It is in need of a more dedicated maintainer.

If you want to be the maintainer of Mopidy-MPRIS, please:

1. Make 2-3 good pull requests improving any part of the project.

2. Read and get familiar with all of the project's open issues.

3. Send a pull request removing this section and adding yourself as the
   "Current maintainer" in the "Credits" section below. In the pull request
   description, please refer to the previous pull requests and state that
   you've familiarized yourself with the open issues.

As a maintainer, you'll be given push access to the repo and the authority to
make releases to PyPI when you see fit.


## Installation

Install by running:

```sh
python3 -m pip install mopidy-mpris
```

See https://mopidy.com/ext/mpris/ for alternative installation methods.


## Configuration

No configuration is required for the MPRIS extension to work.

The following configuration values are available:

- `mpris/enabled`: If the MPRIS extension should be enabled or not.
  Defaults to ``true``.

- `mpris/bus_type`: The type of D-Bus bus Mopidy-MPRIS should connect to.
  Choices include `session` (the default) and `system`.
  
  
## Usage

Once Mopidy-MPRIS has been installed and your Mopidy server has been
restarted, the Mopidy-MPRIS extension announces its presence on D-Bus so that
any MPRIS compatible clients on your system can interact with it. Exactly how
you control Mopidy through MPRIS depends on which MPRIS client you use.


## Clients

The following clients have been tested with Mopidy-MPRIS.

### GNOME Shell builtin

- State: Not working
- Tested versions:
    - Ubuntu 18.10,
    - GNOME Shell 3.30.1-2ubuntu1,
    - Mopidy-MPRIS 2.0.0

GNOME Shell, which is the default desktop on Ubuntu 18.04 onwards, has a
builtin MPRIS client. This client seems to work well with Spotify's player,
but Mopidy-MPRIS does not show up here.

If you have any tips on what's missing to get this working, please open an
issue.

### gnome-shell-extensions-mediaplayer

- State: Working
- Tested versions:
    - Ubuntu 18.10,
    - GNOME Shell 3.30.1-2ubuntu1,
    - gnome-shell-extension-mediaplayer 63,
    - Mopidy-MPRIS 2.0.0
- Website: https://github.com/JasonLG1979/gnome-shell-extensions-mediaplayer

gnome-shell-extensions-mediaplayer is a quite feature rich MPRIS client
built as an extension to GNOME Shell. With the improvements to Mopidy-MPRIS
in v2.0, this extension works very well with Mopidy.

### gnome-shell-extensions-mpris-indicator-button

- State: Working
- Tested versions:
    - Ubuntu 18.10,
    - GNOME Shell 3.30.1-2ubuntu1,
    - gnome-shell-extensions-mpris-indicator-button 5,
    - Mopidy-MPRIS 2.0.0
- Website:
  https://github.com/JasonLG1979/gnome-shell-extensions-mpris-indicator-button/

gnome-shell-extensions-mpris-indicator-button is a minimalistic version of
gnome-shell-extensions-mediaplayer. It works with Mopidy-MPRIS, with the
exception of the play/pause button not changing state when Mopidy starts
playing.

If you have any tips on what's missing to get the play/pause button display
correctly, please open an issue.

### Ubuntu Sound Menu

- State: Unknown

Historically, Ubuntu Sound Menu was the primary target for Mopidy-MPRIS'
development. Since Ubuntu 18.04 replaced Unity with GNOME Shell, this is no
longer the case. It is currently unknown to what degree Mopidy-MPRIS works
with old Ubuntu setups.

If you run an Ubuntu setup with Unity and have tested Mopidy-MPRIS, please
open an issue to share your results.


## Advanced setups

### Running as a service

If you have input on how to best configure Mopidy-MPRIS when Mopidy is
running as a service, please add a comment to
[issue #15](https://github.com/mopidy/mopidy-mpris/issues/15).

### MPRIS on the system bus

You can set the `mpris/bus_type` config value to `system`. This will lead
to Mopidy-MPRIS making itself available on the system bus instead of the
logged in user's session bus.

> [!NOTE]
> Few MPRIS clients will try to access MPRIS devices on the system bus, so
> this will give you limited functionality. For example, media keys in
> GNOME Shell does not work with media players that expose their MPRIS
> interface on the system bus instead of the user's session bus.

The default setup will often not permit Mopidy to publish its service on the
D-Bus system bus, causing a warning similar to this in Mopidy's log:

```
MPRIS frontend setup failed (g-dbus-error-quark:
GDBus.Error:org.freedesktop.DBus.Error.AccessDenied: Connection ":1.3071"
is not allowed to own the service "org.mpris.MediaPlayer2.mopidy" due to
security policies in the configuration file (9))
```

To solve this, create the file
`/etc/dbus-1/system.d/org.mpris.MediaPlayer2.mopidy.conf` with the
following contents:

```xml
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
```

If you run Mopidy as another user than `mopidy`, you must
update `user="mopidy"` in the above file accordingly.

Once the file is in place, you must restart Mopidy for the change to take
effect.

To test the setup, you can run the following command as any user on the
system to play/pause the music:

```sh
dbus-send --system --print-reply \
  --dest=org.mpris.MediaPlayer2.mopidy \
  /org/mpris/MediaPlayer2 \
  org.mpris.MediaPlayer2.Player.PlayPause
```

### UPnP/DLNA with Rygel

[Rygel](https://wiki.gnome.org/Projects/Rygel) is an application that will
translate between Mopidy's MPRIS interface and UPnP. Rygel must be run on the
same machine as Mopidy, but will make Mopidy controllable by any device on the
local network that can control a UPnP/DLNA MediaRenderer.

The setup process is approximately as follows:

1.  Install Rygel.

    On Debian/Ubuntu:

    ```sh
    sudo apt install rygel
    ```

2.  Enable Rygel's MPRIS plugin.

    On Debian/Ubuntu, edit `/etc/rygel.conf`, find the `[MPRIS]`
    section, and change `enabled=false` to `enabled=true`.

3.  Start Rygel.

    To start it as the current user::

    ```sh
    systemctl --user start rygel
    ```

    To make Rygel start as the current user on boot::

    ```sh
    systemctl --user enable rygel
    ```

4.  Configure your system's firewall to allow the local network to reach
    Rygel. Exactly how is out of scope for this document.

5.  Start Mopidy with Mopidy-MPRIS enabled.

6.  If you view Rygel's log output with::

    ```sh
    journalctl --user -feu rygel
    ```

    You should see a log statement similar to::

    ```
    New plugin "org.mpris.MediaPlayer2.mopidy" available
    ```

6.  If everything went well, you should now be able to control Mopidy from a
    device on your local network that can control an UPnP/DLNA MediaRenderer,
    for example the Android app BubbleUPnP.

Alternatively, [upmpdcli combined with
Mopidy-MPD](https://docs.mopidy.com/en/latest/clients/upnp/) serves the same
purpose as this setup.



## Project resources

- [Source code](https://github.com/mopidy/mopidy-mpris)
- [Issues](https://github.com/mopidy/mopidy-mpris/issues)
- [Releases](https://github.com/mopidy/mopidy-mpris/releases)


## Development

### Set up development environment

Clone the repo using, e.g. using [gh](https://cli.github.com/):

```sh
gh repo clone mopidy/mopidy-mpris
```

Enter the directory, and install dependencies using [uv](https://docs.astral.sh/uv/):

```sh
cd mopidy-mpris/
uv sync
```

### Running tests

To run all tests and linters in isolated environments, use
[tox](https://tox.wiki/):

```sh
tox
```

To only run tests, use [pytest](https://pytest.org/):

```sh
pytest
```

To format the code, use [ruff](https://docs.astral.sh/ruff/):

```sh
ruff format .
```

To check for lints with ruff, run:

```sh
ruff check .
```

To check for type errors, use [pyright](https://microsoft.github.io/pyright/):

```sh
pyright .
```

### Adding features and fixing bugs

Mopidy-MPRIS has an extensive test suite, so the first step for all changes
or additions is to add a test exercising the new code. However, making the
tests pass doesn't ensure that what comes out on the D-Bus bus is correct. To
introspect this through the bus, there's a couple of useful tools.

### Browsing the MPRIS API with D-Feet

D-Feet is a graphical D-Bus browser. On Debian/Ubuntu systems it can be
installed by running:

```sh
sudo apt install d-feet
```

Then run the `d-feet` command. In the D-Feet window, select the tab
corresponding to the bus you run Mopidy-MPRIS on, usually the session bus.
Then search for "MediaPlayer2" to find all available MPRIS interfaces.

To get the current value of a property, double-click it. To execute a method,
double-click it, provide any required arguments, and click "Execute".

For more information on D-Feet, see the
[GNOME wiki](https://wiki.gnome.org/Apps/DFeet).

### Testing the MPRIS API with pydbus

To use the MPRIS API directly, start Mopidy, and then run the following in a
Python shell to use `pydbus` as an MPRIS client:

```pycon
>>> import pydbus
>>> bus = pydbus.SessionBus()
>>> player = bus.get('org.mpris.MediaPlayer2.mopidy', '/org/mpris/MediaPlayer2')
```

Now you can control Mopidy through the player object. To get properties from
Mopidy, run for example:

```pycon
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
```

To pause Mopidy's playback through D-Bus, run:

```pycon
>>> player.Pause()
>>>
```

For details on the API, please refer to the
[MPRIS specification](https://specifications.freedesktop.org/mpris-spec/latest/).

### Making a release

To make a release to PyPI, go to the project's [GitHub releases
page](https://github.com/mopidy/mopidy-mpris/releases)
and click the "Draft a new release" button.

In the "choose a tag" dropdown, select the tag you want to release or create a
new tag, e.g. `v0.1.0`. Add a title, e.g. `v0.1.0`, and a description of the changes.

Decide if the release is a pre-release (alpha, beta, or release candidate) or
should be marked as the latest release, and click "Publish release".

Once the release is created, the `release.yml` GitHub Action will automatically
build and publish the release to
[PyPI](https://pypi.org/project/mopidy-mpris/).


## Credits

- Original author: [Stein Magnus Jodal](https://github.com/mopidy)
- Current maintainer: None. Maintainer wanted, see section above.
- [Contributors](https://github.com/mopidy/mopidy-mpris/graphs/contributors)
