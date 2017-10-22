from dashboard.server import WidgetServer
from uvhttp.dns import Resolver
import asyncio
import argparse

async def main(settings=None):
    widgets = WidgetServer('dashboard/widgets', settings=settings, resolver=Resolver(asyncio.get_event_loop(), ipv6=False))
    await widgets.start()
    return widgets

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
