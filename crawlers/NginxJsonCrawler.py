from urllib.parse import urljoin, unquote

from pydantic import HttpUrl

from accessors.Accessor import Accessor
from crawlers.Crawler import Crawler
from entities import Folder, File
import asyncio


class NginxJsonCrawler(Crawler):
    def __init__(self):
        self.accessor = None

    async def crawl(self, url: HttpUrl, accessor: Accessor) -> Folder:
        print(f"Crawling {url}")

        # Store accessor for recursive calls
        self.accessor = accessor

        # Ensure URL ends with a slash
        if not url.path.endswith("/"):
            url = HttpUrl(str(url) + "/")

        # Try to fetch index.json
        index_url = urljoin(str(url), "index.json")
        async with accessor.get(index_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch {index_url}: {response.status}")

            entries = await response.json()
            return await self._process_current_folder(url, entries)

    async def _process_current_folder(self, url: HttpUrl, entries: list) -> Folder:
        files = []
        pending_folder_urls = []

        # Extract folder name from URL
        folder_name = unquote(url.path.rstrip("/").split("/")[-1])

        for entry in entries:
            if entry["type"] == "directory":
                folder_url = HttpUrl(urljoin(str(url), entry["name"]))
                pending_folder_urls.append(folder_url)
            elif entry["type"] == "file":
                file_url = HttpUrl(urljoin(str(url), entry["name"]))
                files.append(File(name=unquote(entry["name"]), url=file_url))

        folders = await asyncio.gather(
            *[
                self.crawl(folder_url, self.accessor)
                for folder_url in pending_folder_urls
            ]
        )

        return Folder(
            name=folder_name,
            folders=folders,
            files=files,
        )
