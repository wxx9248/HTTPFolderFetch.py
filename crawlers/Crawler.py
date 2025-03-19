from abc import ABC, abstractmethod

from pydantic import HttpUrl

from accessors.Accessor import Accessor
from entities import Folder


class Crawler(ABC):
    @abstractmethod
    async def crawl(self, url: HttpUrl, accessor: Accessor) -> Folder:
        pass
