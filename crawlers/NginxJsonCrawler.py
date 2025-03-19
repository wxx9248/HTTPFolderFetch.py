from urllib.parse import urljoin, unquote

from accessors.Accessor import Accessor
from crawlers.Crawler import Crawler
from entities import Folder, File
import asyncio


class NginxJsonCrawler(Crawler):
    def __init__(self):
        self.accessor = None

    async def crawl(self, url: str, accessor: Accessor) -> Folder:
        print(f"Crawling {url}")

        # Store accessor for recursive calls
        self.accessor = accessor

        # Ensure URL ends with a slash
        if not url.endswith("/"):
            url += "/"

        # Try to fetch index.json
        index_url = urljoin(url, "index.json")
        try:
            async with accessor.get(index_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch {index_url}: {response.status}")

                data = await response.json()
                return await self._process_directory(url, data)
        except Exception as e:
            raise Exception(f"Error crawling {url}: {str(e)}")

    async def _process_directory(self, base_url: str, entries: list) -> Folder:
        files = []

        pending_folder_urls = []

        for entry in entries:
            if entry["type"] == "directory":
                folder_url = urljoin(base_url, entry["name"])
                pending_folder_urls.append(folder_url)
            elif entry["type"] == "file":
                file_url = urljoin(base_url, entry["name"])
                files.append(File(name=unquote(entry["name"]), url=file_url))

        folders = await asyncio.gather(
            *[
                self.crawl(folder_url, self.accessor)
                for folder_url in pending_folder_urls
            ]
        )

        return Folder(
            name=unquote(base_url.rstrip("/").split("/")[-1]),
            folders=folders,
            files=files,
        )
