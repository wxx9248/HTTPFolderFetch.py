from abc import ABC, abstractmethod

from pydantic import HttpUrl

from entities import Folder


class Strategy(ABC):
    @abstractmethod
    async def execute(self, url: HttpUrl) -> Folder:
        pass
