from dashboard.sonos import Sonos
import asyncio
import uvhttp.http

class WidgetContext:
    """
    Context that is passed as an argument to widgets when they are called.
    
    The context contains methods useful for widgets.
    """
    def __init__(self):
        self.__sonos = None
        self.__client = None

    @property
    def client(self):
        """
        A :class:`uvhttp.http.Session` that can be used for
        making HTTP requests::

            async def ip_widget(wc):
                response = await wc.client.get(b'http://httpbin.org/ip')
                return { "ip": response.json()["origin"] }
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
        The :class:`dashboard.sonos.Sonos` client that can be used by widgets.
        """
        if not self.__sonos:
            self.__sonos = Sonos(self.client)

        return self.__sonos

    @sonos.setter
    def sonos(self, sonos):
        self.__sonos = sonos
