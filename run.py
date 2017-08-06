from dashboard.server import WidgetServer
import asyncio

async def main():
    widgets = WidgetServer('dashboard/widgets')
    await widgets.start()
    return widgets

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
