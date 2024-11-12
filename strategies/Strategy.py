from abc import ABC, abstractmethod

from entities import Folder


class Strategy(ABC):
    @abstractmethod
    async def execute(self, url: str) -> Folder:
        pass
