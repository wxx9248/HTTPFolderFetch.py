import aiohttp

from accessors.Accessor import Accessor


class PlainAccessor(Accessor):
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get(self, url: str):
        if not self.session:
            self.session = aiohttp.ClientSession()

        return self.session.get(url)
