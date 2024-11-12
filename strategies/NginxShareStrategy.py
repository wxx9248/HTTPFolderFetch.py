from accessors import PlainAccessor
from crawlers import NginxJsonCrawler
from entities import Folder
from strategies.Strategy import Strategy


class NginxShareStrategy(Strategy):
    def __init__(self):
        self.crawler = NginxJsonCrawler()
        self.accessor = PlainAccessor()

    async def execute(self, url: str) -> Folder:
        async with self.accessor:
            return await self.crawler.crawl(url, self.accessor)
