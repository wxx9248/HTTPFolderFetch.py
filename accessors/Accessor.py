from abc import ABC, abstractmethod

import aiohttp


class Accessor(ABC):
    @abstractmethod
    async def get(self, url: str) -> aiohttp.ClientResponse:
        pass
