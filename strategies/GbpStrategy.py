from accessors import PlainAccessor
from crawlers import GbpHttpCrawler
from entities import Folder
from strategies.Strategy import Strategy


class GbpStrategy(Strategy):
    def __init__(self):
        self.crawler = GbpHttpCrawler()
        self.accessor = PlainAccessor()

    async def execute(self, url: str) -> Folder:
        async with self.accessor:
            return await self.crawler.crawl(url, self.accessor)
