import socket
from dashboard.utils import get_default_gateway

class Sonos:
    """
    A module for querying the `node.js Sonos API`_::

        sonos = Sonos(uvhttp.session.Session(5, asyncio.get_event_loop()))
        zones = await sonos.api('zones')
        print(zones)

    It will automatically find the API if it is reachable on localhost, the default
    gateway, or ``docker.for.mac.local``. If it is not one of these, it should be indicated
    in the ``api_host`` argument.

    .. _node.js Sonos API: https://github.com/jishi/node-sonos-web-controller
    """
    def __init__(self, session, api_host=None, api_base=None):
        self.session = session

        self.api_host = api_host
        self.api_base = api_base or 'http://{}:5005/'

    async def find_api(self):
        """
        Find the Sonos API running on localhost or the host server.
        """
        if self.api_host:
            return

        addrs = [ '127.0.0.1', get_default_gateway() ]

        try:
            addrs.insert(0, socket.gethostbyname('docker.for.mac.localhost'))
        except socket.gaierror:
            pass

        for addr in addrs:
            try:
                import logging
                logging.error(addr)
                await self.session.get(self.api_base.format(addr).encode())
                self.api_host = addr
                break
            except ConnectionRefusedError:
                pass

    async def api(self, method):
        """
        Make a request to the Sonos API, returning the JSON.
        """
        await self.find_api()
        response = await self.session.get((self.api_base.format(self.api_host) + method).encode())
        return response.json()
