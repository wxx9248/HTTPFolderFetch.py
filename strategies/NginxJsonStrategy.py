from pydantic import HttpUrl

from accessors import PlainAccessor
from crawlers import NginxJsonCrawler
from entities import Folder
from strategies.Strategy import Strategy


class NginxJsonStrategy(Strategy):
    def __init__(self):
        self.crawler = NginxJsonCrawler()
        self.accessor = PlainAccessor()

    async def execute(self, url: HttpUrl) -> Folder:
        async with self.accessor:
            return await self.crawler.crawl(url, self.accessor)
