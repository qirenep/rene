import aiohttp


class PlayerNotFound(Exception):
    """Exception raised when a player is not found."""

    pass


class RequestError(Exception):
    """Exception raised when it is a request error."""

    pass


class Fetch:

    def __init__(self, platform, name):
        self.platform = platform
        self.name = name

    async def fetch(self):
        """Retrieves players stats from the API."""
        URL = f"https://ow-api.com/v2/stats/{self.platform}/{self.name}/complete"

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(URL) as r:
                if r.status == 200:
                    return await r.json()
                else:
                    raise RequestError()

    async def data(self):
        """Returns players data."""
        try:
            r = await self.fetch()
            return r
        except Exception:
            raise PlayerNotFound()
