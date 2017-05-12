# Radio Export

This script integrates with the Spotify API to turn your favorite
radio station into a Spotify playlist. This is useful if

1. you don't have access to the radio station (e.g. you live in a different city)
2. you want to take your radio station offline with you (e.g. on a run)
3. you don't feel like listening to commericals

I currently have it set to integrate with my favorite radio station, [WXPN](http://www.xpn.org/).

You can listen to that station here: [XPN Live](https://open.spotify.com/user/12758562/playlist/1PojFHqjnLoHWrBBQNoNYO)

## Adding new stations

If you would like to integrate a new radio station (or any feed of music), just add a new module to `radio_export/stations` with a function called `get_current_songs` which
returns a list of `Song` objects (see `radio_export/song`).

Then, run the following:

    radio-export \
        --station <name of module> \
        --playlist-name <name of spotify playlist>

It will populate the playlist with the songs returned by `radio_export/stations/<name of station>:get_current_songs`
