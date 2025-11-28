from pydantic import HttpUrl

from accessors import BehavedAccessor
from crawlers.KhinsiderCrawler import KhinsiderHttpCrawler
from entities import Folder
from strategies.Strategy import Strategy


class KhinsiderStrategy(Strategy):
    def __init__(self):
        self.crawler = KhinsiderHttpCrawler()
        self.accessor = BehavedAccessor()

    async def execute(self, url: HttpUrl) -> Folder:
        async with self.accessor:
            return await self.crawler.crawl(url, self.accessor)
