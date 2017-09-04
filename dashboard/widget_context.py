from dashboard.sonos import Sonos
import concurrent.futures
import asyncio
import uvhttp.http
from uvhue.uvhue import Hue

class WidgetContext:
    """
    Context that is passed as an argument to widgets when they are called.
    
    The context contains methods useful for widgets.
    """
    def __init__(self, resolver=None, settings=None):
        self.__sonos = None
        self.__client = None
        self.__hue = None
        self.resolver = resolver
        self.settings = settings
        self.party_mode = False
        self.executor = concurrent.futures.ProcessPoolExecutor()

    async def run(self, func, *args):
        """
        Run a function in an external process if it is CPU intensive.
        """
        return await asyncio.get_event_loop().run_in_executor(self.executor, func, *args)

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
            self.__client = uvhttp.http.Session(10, asyncio.get_event_loop(), resolver=self.resolver)

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

    @property
    def hue(self):
        """
        The :class:`uvhue.uvhue.Hue` client that can be used by widgets.
        """
        if not self.__hue:
            hue_api = self.settings['hue_address'].encode()
            self.__hue = Hue(asyncio.get_event_loop(), hue_api, resolver=self.resolver)
            self.__hue.hue_id = self.settings['hue_token']

        return self.__hue

    @hue.setter
    def hue(self, hue):
        self.__hue = hue

    def close(self):
        self.executor.shutdown()
