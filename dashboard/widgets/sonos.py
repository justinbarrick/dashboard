from dashboard.widget import *
from uvhue.rgb import rgb_to_xy
import asyncio
import datetime
import logging
import uvhttp.http

@refresh_every(3)
async def sonos_widget(request, ws):
    """
    Return the now playing information from Sonos.
    """

    zones = await ws.sonos.api('zones')

    zone_info = []
    for zone in zones:
        zone_info.append({
            "name": zone['coordinator']['roomName'],
            "state": {
                "state": zone['coordinator']['state']['playbackState'],
                "currentTrack":  zone['coordinator']['state']['currentTrack'],
                "tv": zone['coordinator']['state']['currentTrack']['type'] == 'line_in',
                "volume": zone['coordinator']['state']['volume'],
                "elapsed": zone['coordinator']['state']['elapsedTime']
            },
        })

    return {
        "speakers": zone_info
    }

async def pause_sonos_widget(request, wc):
    """
    Pause the Sonos system.
    """
    zones = await wc.sonos.api('zones')

    errors = []
    for zone in zones:
        name = zone['coordinator']['roomName'].replace(' ', '%20')

        response = await wc.sonos.api('{}/pause'.format(name))
        if response.get("status") != "success":
            errors.append("could not pause {}: {}".format(name, str(response)))

    return {
        "result": "paused all speakers",
        "errors": errors
    }

@methods(['POST'])
async def play_sonos_widget(request, wc, args):
    """
    Play the Sonos system.
    """
    room = args['room']

    zones = await wc.sonos.api('zones')

    errors = []
    for zone in zones:
        if zone['coordinator']['roomName'].lower() != room.lower():
            continue

        name = zone['coordinator']['roomName'].replace(' ', '%20')
        response = await wc.sonos.api('{}/play'.format(name))
        if response.get("status") != "success":
            errors.append("could not play {}: {}".format(name, str(response)))
        else:
            return { "result": "played the {}".format(room) }

    return {
        "status": "error",
        "errors": errors
    }

@methods(['POST'])
async def party_mode_widget(request, wc):
    if not wc.party_mode:
        wc.party_mode = True
        await play_sonos_widget(request, wc, {"room": "Living Room"})
    else:
        await pause_sonos_widget(request, wc)
        wc.party_mode = False

    return {
        "party_mode": wc.party_mode
    }

@methods(['POST'])
async def sonos_hue_widget(request, wc, args):
    logging.error('Args were: {}'.format(str(args)))

    if args['type'] != 'transport-state':
        return {}

    data = args['data']

    results = {
        "album_art_uri": data['state']['currentTrack'].get('absoluteAlbumArtUri'),
        "room": data['roomName'],
        "state": data['state']['playbackState'],
        "rgb": []
    }

    if results['room'] != 'Living Room':
        return {}

    if results['state'] == 'PLAYING' and results['album_art_uri']:
        image = await wc.client.get(results['album_art_uri'].encode())
        rgb = await wc.client.post(wc.settings['img_processing_api'].encode(), data=image.content)
        rgb_value = rgb.json()["rgb"]
    else:
        rgb_value = [255, 255, 255]

    results['rgb'] = rgb_value

    if wc.party_mode:
        light_result = await wc.hue.set_states({"xy": rgb_to_xy(rgb_value)})
        results["light_result"] = light_result

    return results
