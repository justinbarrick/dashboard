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
