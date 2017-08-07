from dashboard.sonos import Sonos
import asyncio
import uvhttp.http

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
