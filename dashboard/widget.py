from dashboard.sonos import Sonos
import asyncio
import functools
import uvhttp.http

def refresh_every(frequency):
    """
    Widget wrapper that sets the widget to refresh every ``frequency`` seconds.

    The ``frequency`` is available as ``frequency`` in the widget options in the index
    template.

    A widget with a ``frequency`` of ``None`` should be refreshed at the default interval.
    A widget with a ``frequency`` of ``0`` should never be refreshed.
    A widget with a ``frequency`` of ``n`` should be refreshed every ``n`` seconds.
    """
    def wrapper(func):
        @functools.wraps(func)
        async def real_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        real_wrapper.frequency = frequency
        return real_wrapper

    return wrapper

class WidgetContext:
    def __init__(self):
        """
        Context that is passed to widgets when they are called.
        """
        self.__sonos = None
        self.__client = None

    @property
    def client(self):
        """
        A uvhttp client Session that can be used for making HTTP requests.
        """
        if not self.__client:
            self.__client = uvhttp.http.Session(10, asyncio.get_event_loop())

        return self.__client

    @client.setter
    def client(self, client):
        self.__client = client

    @property
    def sonos(self):
        """
        The Sonos client that can be used by widgets.
        """
        if not self.__sonos:
            self.__sonos = Sonos(self.client)

        return self.__sonos

    @sonos.setter
    def sonos(self, sonos):
        self.__sonos = sonos
