from urllib.parse import urljoin, unquote

from bs4 import BeautifulSoup

from accessors.Accessor import Accessor
from crawlers.Crawler import Crawler
from entities import Folder, File
import asyncio


class GbpHttpCrawler(Crawler):
    def __init__(self):
        self.accessor = None

    async def crawl(self, url: str, accessor: Accessor) -> Folder:
        print(f"Crawling {url}")

        # Store accessor for recursive calls
        self.accessor = accessor

        # Ensure URL ends with a slash
        if not url.endswith("/"):
            url += "/"

        try:
            async with accessor.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch {url}: {response.status}")

                # Get the HTML content
                html_content = await response.text()

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, "html.parser")

                # Extract folder name from URL
                folder_name = url.rstrip("/").split("/")[-1]
                if not folder_name:
                    folder_name = "root"  # Default name if URL ends with domain

                # Find the table containing files and folders
                table = soup.find("table", id="table")
                if not table:
                    raise Exception(f"Table with file listing not found in {url}")

                # Parse the table and return the folder structure
                return await self._parse_table(url, table, folder_name)

        except Exception as e:
            raise Exception(f"Error crawling {url}: {str(e)}")

    async def _parse_table(self, base_url: str, table, folder_name: str) -> Folder:
        files = []
        pending_folder_urls = []

        # Find all rows in the table body
        rows = table.find_all("tr")

        # Skip the header row and the parent directory row (..)
        for row in rows[2:]:  # Skip header row and parent directory
            cells = row.find_all("td")
            if not cells:
                continue

            # Get the link cell (first cell)
            link_cell = cells[0]
            link = link_cell.find("a")

            if not link:
                continue

            href = link.get("href")
            name = link.text

            # Check if it's a folder or file
            if name.endswith("/"):
                # It's a folder - remove the trailing slash for the name
                folder_name = name[:-1]
                folder_url = urljoin(base_url, href)

                # Recursively crawl the subfolder
                pending_folder_urls.append(folder_url)
            else:
                # It's a file
                file_url = urljoin(base_url, href)
                files.append(File(name=unquote(name), url=file_url))

        folders = await asyncio.gather(
            *[
                self.crawl(folder_url, self.accessor)
                for folder_url in pending_folder_urls
            ]
        )

        return Folder(name=unquote(folder_name), folders=folders, files=files)
