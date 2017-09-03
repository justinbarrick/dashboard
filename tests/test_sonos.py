from uvhue.utils import HueServer
from uvhttp.utils import http_server, http_server_no_loop
from dashboard.sonos import Sonos
from nose.tools import *
from test_utils import *
import functools
from sanic import Sanic
from sanic.response import json, html

def speaker(state=None, members=None, tv=False, music=False, elapsed=None):
    speaker_config = {
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
                    "artist": "",
                    "album": "",
                    "albumArtUri": "",
                    "absoluteAlbumArtUri": "",
                    "uri": "",
                    "title": "",
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

    if members:
        speaker_config['members'] = members

    if state:
        speaker_config['coordinator']['state']['playbackState'] = state

    if tv:
        speaker_config['coordinator']['state']['currentTrack'] = {
            "duration": 0,
            "uri": "x-sonos-htastream:RINCON:spdif",
            "type": "line_in",
            "stationName": ""
        }

    if music:
        speaker_config['coordinator']['state']['currentTrack'] = {
            "duration": 123,
            "artist": "Lady Gaga",
            "album": "Lady Gaga Album",
            "albumArtUri": "/lady_gaga.jpg",
            "absoluteAlbumArtUri": "https://sonos/lady_gaga.jpg",
            "uri": "spotify:hello",
            "title": "Pokerface",
            "stationName": "",
            "type": "track"
        }

    if elapsed:
        speaker_config['coordinator']['state']['elapsedTime'] = elapsed
        speaker_config['coordinator']['state']['elapsedTimeFormatted'] = str(datetime.timedelta(seconds=elapsed))

    return speaker_config

def with_sonos(*speakers):
    def real_with_sonos(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            app = Sanic(log_config=None)
            app.config.LOGO = None

            @app.route('/')
            async def index(request):
                return html('<html></html>')

            @app.route('/zones')
            async def zones(request):
                return json(speakers or [speaker()])

            @app.route('/<name>/<action>')
            async def action(request, name, action):
                return json({
                    "status": "success", "name": name, "action": action
                })

            @app.route('/aaaa_album_art')
            async def album(request):
                return json({})

            @app.route('/image', methods=['POST'])
            async def image(request):
                return json({"rgb": (1,1,1)})

            server = await app.create_server(host='0.0.0.0', port=5005, log_config=None)

            try:
                return await func(*args, **kwargs)
            finally:
                server.close()

        return wrapper

    return real_with_sonos

@start_widgets('dashboard/widgets')
@with_sonos()
@with_client
async def test_sonos_zones(client, widgets):
    s = Sonos(client)

    zones = await s.api('zones')
    zone_names = list(map(lambda x: x['coordinator']['roomName'], zones))
    assert_equal(zone_names, ['Living Room'])

@start_widgets('dashboard/widgets')
@with_sonos()
@with_client
async def test_sonos_widget_stopped(client, widgets):
    response = await request_widget(client, 'sonos')
    assert_equal(response.json(), { "speakers": [ {
        "name": "Living Room",
        "state": {
            "state": "STOPPED",
            "tv": False,
            "currentTrack": {
                "duration": 0,
                "artist": "",
                "album": "",
                "albumArtUri": "",
                "absoluteAlbumArtUri": "",
                "uri": "",
                "title": "",
                "stationName": "",
                "type": "track"
            },
            "volume": 11,
            "elapsed": 0
        }
    } ] })

    response = await request_widget(client, 'sonos', False)
    assert_in('<span class="nowPlayingInfo trackTitle"></span>', response.text)
    assert_in('<span class="nowPlayingInfo artistTitle"></span>', response.text)
    assert_in('<span class="nowPlayingInfo albumTitle"></span>', response.text)
    assert_in('background-image: url()', response.text)

@start_widgets('dashboard/widgets')
@with_sonos(speaker(state="PLAYING", music=True))
@with_client
async def test_sonos_widget_music(client, widgets):
    response = await request_widget(client, 'sonos')
    assert_equal(response.json(), { "speakers": [ {
        "name": "Living Room",
        "state": {
            "state": "PLAYING",
            "tv": False,
            "currentTrack": {
                "duration": 123,
                "artist": "Lady Gaga",
                "album": "Lady Gaga Album",
                "albumArtUri": "/lady_gaga.jpg",
                "absoluteAlbumArtUri": "https://sonos/lady_gaga.jpg",
                "uri": "spotify:hello",
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

@start_widgets('dashboard/widgets')
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_tv(client, widgets):
    response = await request_widget(client, 'sonos')
    assert_equal(response.json(), { "speakers": [ {
        "name": "Living Room",
        "state": {
            "state": "PLAYING",
            "currentTrack": {
                "duration": 0,
                "uri": "x-sonos-htastream:RINCON:spdif",
                "type": "line_in",
                "stationName": ""
            },
            "tv": True,
            "volume": 11,
            "elapsed": 0
        }
    } ] })

    response = await request_widget(client, 'sonos', False)
    assert_in('<span class="nowPlayingInfo trackTitle">TV</span>', response.text)

@start_widgets('dashboard/widgets')
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_pause(client, widgets):
    response = await request_widget(client, 'pause_sonos')
    assert_equal(response.json(), { "result": "paused all speakers", "errors": [] })

@start_widgets('dashboard/widgets')
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_play(client, widgets):
    response = await request_widget(client, 'play_sonos', args={
        'room': 'Living Room'
    })

    assert_equal(response.json(), { "result": "played the Living Room"  })

@start_widgets('dashboard/widgets')
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_party_mode(client, widgets):
    response = await request_widget(client, 'party_mode')
    assert_equal(response.json(), { "party_mode": True })

    response = await request_widget(client, 'party_mode')
    assert_equal(response.json(), { "party_mode": False })

def create_state(tv=False, paused=False):
    playback = 'PLAYING' if not paused else 'PAUSED'

    state = {
        'type': 'transport-state',
        'data': {
            'uuid': 'hello',
            'coordinator': 'hello',
            'avTransportUriMetadata': '', 
            'state': {
                'playbackState': playback,
                'trackNo': 1, 'mute': False, 
                'playMode': {
                    'shuffle': False, 'repeat': 'none',
                    'crossfade': False
                }, 
            'elapsedTimeFormatted': '00:01:34',
            'nextTrack': {
                'artist': 'Marshmello',
                'title': 'Silence (feat. Khalid)',
                'album': 'Silence (feat. Khalid) - Single',
                'albumArtUri': '/aaaa_album_art',
                'duration': 180,
                'absoluteAlbumArtUri': 'http://127.0.0.1:5005/aaaa_album_art',
                'uri': 'x-sonos-http:librarytrack%3aa.1268152499.mp4?sid=204&flags=8224&sn=1'},
            'elapsedTime': 94,
            'volume': 24,
            'equalizer': {
                'speechEnhancement': True,
                'bass': 7,
                'nightMode': False,
                'loudness': True,
                'treble': 0
            },
            'currentTrack': {
                'artist': 'Taylor Swift',
                'title': 'Look What You Made Me Do',
                'type': 'track',
                'album': 'Look What You Made Me Do - Single',
                'albumArtUri': '/aaaa_album_art',
                'duration': 211,
                'stationName': '', 
                'absoluteAlbumArtUri': 'http://127.0.0.1:5005/aaaa_album_art',
                'uri': 'x-sonos-http:librarytrack%3aa.1275004357.mp4?sid=204&flags=8224&sn=1'}
            },
            'avTransportUri': 'x-rincon-queue:RINCON_B8E937409D0901400#0',
            'groupState': {
                'volume': 24,
                'mute': False
            },
            'roomName': 'Living Room'
        }
    }

    if tv:
        state['data']['state']['currentTrack'] = {
            "duration": 0,
            "uri": "x-sonos-htastream:RINCON:spdif",
            "type": "line_in",
            "stationName": ""
        }

    return state

@start_widgets('dashboard/widgets')
@http_server_no_loop(HueServer)
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_hue_integration(client, hue_server, widgets):
    hue_server.valid_users.append(widgets.settings['hue_token'])

    widgets.resolver.add_to_cache(b'hue', 80, hue_server.host.encode(), 60, port=hue_server.port)
    response = await request_widget(client, 'sonos_hue', args=create_state())
    assert_equal(response.json(), {
        "album_art_uri": "http://127.0.0.1:5005/aaaa_album_art",
        "room": "Living Room",
        "state": "PLAYING",
        "light_result": False,
        "rgb": [1, 1, 1]
    })

@start_widgets('dashboard/widgets')
@http_server_no_loop(HueServer)
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_hue_integration_tv(client, hue_server, widgets):
    hue_server.valid_users.append(widgets.settings['hue_token'])

    widgets.resolver.add_to_cache(b'hue', 80, hue_server.host.encode(), 60, port=hue_server.port)
    response = await request_widget(client, 'sonos_hue', args=create_state(tv=True))
    assert_equal(response.json(), {
        "album_art_uri": None,
        "room": "Living Room",
        "state": "PLAYING",
        "light_result": False,
        "rgb": [255, 255, 255]
    })

@start_widgets('dashboard/widgets')
@http_server_no_loop(HueServer)
@with_sonos(speaker(state="PLAYING", tv=True))
@with_client
async def test_sonos_widget_hue_integration_pause(client, hue_server, widgets):
    hue_server.valid_users.append(widgets.settings['hue_token'])

    widgets.resolver.add_to_cache(b'hue', 80, hue_server.host.encode(), 60, port=hue_server.port)
    response = await request_widget(client, 'sonos_hue', args=create_state(paused=True))
    assert_equal(response.json(), {
        "album_art_uri": "http://127.0.0.1:5005/aaaa_album_art",
        "room": "Living Room",
        "state": "PAUSED",
        "light_result": False,
        "rgb": [255, 255, 255]
    })
