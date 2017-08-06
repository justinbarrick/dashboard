class Sonos:
    """
    A module for querying the node.js Sonos API
    """
    def __init__(self, session, api):
        self.session = session
        self.api_base = 'http://{}:5005/'.format(api) + '{}'

    async def api(self, method):
        response = await self.session.get(self.api_base.format(method).encode())
        return response.json()
