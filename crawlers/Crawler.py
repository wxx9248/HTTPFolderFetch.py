from abc import ABC, abstractmethod

from accessors.Accessor import Accessor
from entities import Folder


class Crawler(ABC):
    @abstractmethod
    async def crawl(self, url: str, accessor: Accessor) -> Folder:
        pass
