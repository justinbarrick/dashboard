from dashboard.server import WidgetServer
import asyncio
import argparse

from dashboard.utils import get_default_gateway

async def main(sonos_api=None):
    widgets = WidgetServer('dashboard/widgets', sonos_api)
    await widgets.start()
    return widgets

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sonos-api', help='The Sonos API IP.')
    args = parser.parse_args()

    if args.sonos_api == 'gateway':
        sonos_api = get_default_gateway()
    else:
        sonos_api = args.sonos_api

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(sonos_api))
    loop.run_forever()
