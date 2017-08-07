from dashboard.sonos import Sonos
from nose.tools import *
from test_utils import *
import functools
from sanic import Sanic
from sanic.response import json, html

def with_sonos(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        app = Sanic(log_config=None)

        @app.route('/')
        def index(request):
            return html('<html></html>')

        @app.route('/zones')
        def zones(request):
            return json([
                {
                    "members": [
                    ],
                    "coordinator": {
                        "groupState": {
                            "volume": 10,
                            "mute": False
                        },
                        "coordinator": "HI!",
                        "state": {
                            "elapsedTimeFormatted": "00:00:00",
                            "playMode": {
                                "shuffle": False,
                                "crossfade": False,
                                "repeat": "none"
                            },
                            "equalizer": {
                                "base": 3,
                                "loudness": True,
                                "treble": 0,
                                "nightMode": False,
                                "speechEnhancement": True
                            },
                            "mute": False,
                            "currentTrack": {
                                "duration": 0,
                                "artist": "Lady Gaga",
                                "album": "Lady Gaga Album",
                                "albumArtUri": "/lady_gaga.jpg",
                                "absoluteAlbumArtUri": "https://sonos/lady_gaga.jpg",
                                "uri": "",
                                "title": "Pokerface",
                                "stationName": "",
                                "type": "track"
                            },
                            "volume": 11,
                            "elapsedTime": 0,
                            "playbackState": "STOPPED",
                            "nextTrack": {
                                "duration": 0,
                                "artist": "",
                                "album": "",
                                "albumArtUri": "",
                                "uri": "",
                                "title": ""
                            }
                        },
                        "roomName": "Living Room",
                        "uuid": "HI!"
                    },
                    "uuid": "HI!"
                }
            ])

        server = await app.create_server(host='0.0.0.0', port=5005, log_config=None)

        try:
            return await func(*args, **kwargs)
        finally:
            server.close()

    return wrapper

@start_widgets('dashboard/widgets')
@with_sonos
@with_client
async def test_sonos_zones(client, widgets):
    s = Sonos(client)

    zones = await s.api('zones')
    zone_names = list(map(lambda x: x['coordinator']['roomName'], zones))
    assert_equal(zone_names, ['Living Room'])

@start_widgets('dashboard/widgets')
@with_sonos
@with_client
async def test_sonos_widget(client, widgets):
    response = await request_widget(client, 'sonos')
    assert_equal(response.json(), { "speakers": [ {
        "name": "Living Room",
        "state": {
            "state": "STOPPED",
            "currentTrack": {
                "duration": 0,
                "artist": "Lady Gaga",
                "album": "Lady Gaga Album",
                "albumArtUri": "/lady_gaga.jpg",
                "absoluteAlbumArtUri": "https://sonos/lady_gaga.jpg",
                "uri": "",
                "title": "Pokerface",
                "stationName": "",
                "type": "track"
            },
            "volume": 11,
            "elapsed": 0
        }
    } ] })

    response = await request_widget(client, 'sonos', False)
    assert_in('<span class="nowPlayingInfo trackTitle">Pokerface</span>', response.text)
    assert_in('<span class="nowPlayingInfo artistTitle">Lady Gaga</span>', response.text)
    assert_in('<span class="nowPlayingInfo albumTitle">Lady Gaga Album</span>', response.text)
    assert_in('background-image: url(https://sonos/lady_gaga.jpg)', response.text)
