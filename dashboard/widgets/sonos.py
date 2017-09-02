from dashboard.widget import *
import asyncio
import datetime
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
