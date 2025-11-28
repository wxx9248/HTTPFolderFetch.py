import asyncio
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic import HttpUrl

from accessors.Accessor import Accessor
from crawlers.Crawler import Crawler
from entities import Folder, File


class KhinsiderHttpCrawler(Crawler):
    # Format priority: higher index = higher priority
    FORMAT_PRIORITY = ['mp3', 'm4a', 'flac']

    def __init__(self):
        self.accessor = None

    async def crawl(self, url: HttpUrl, accessor: Accessor) -> Folder:
        print(f"Crawling {url}")
        self.accessor = accessor

        html_content = await self._fetch_page(str(url))
        soup = BeautifulSoup(html_content, "html.parser")

        folder_name = self._extract_folder_name(soup)
        song_entries = self._extract_song_entries(soup, url)

        files = await asyncio.gather(*[
            self._process_song_entry(entry)
            for entry in song_entries
        ])

        files = [f for f in files if f is not None]
        return Folder(name=folder_name, folders=[], files=files)

    async def _fetch_page(self, url: str) -> str:
        async with self.accessor.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch {url}: {response.status}")
            return await response.text()

    def _extract_folder_name(self, soup: BeautifulSoup) -> str:
        h2 = soup.find("h2")
        if not h2:
            raise Exception("Could not find folder name (h2 tag)")
        return h2.get_text(strip=True)

    def _extract_song_entries(self, soup: BeautifulSoup, base_url: HttpUrl) -> list[dict]:
        songlist = soup.find("table", id="songlist")
        if not songlist:
            raise Exception("Could not find songlist table")

        entries = []
        seen_urls = set()

        for row in songlist.find_all("tr"):
            if row.get("id") in ["songlist_header", "songlist_footer"]:
                continue

            entry = self._parse_song_row(row, base_url)
            if not entry:
                continue

            if entry["page_url"] in seen_urls:
                continue
            seen_urls.add(entry["page_url"])
            entries.append(entry)

        return entries

    def _parse_song_row(self, row, base_url: HttpUrl) -> dict | None:
        cells = row.find_all("td")
        if len(cells) < 3:
            return None

        track_number = self._extract_track_number(cells)
        if not track_number:
            return None

        clickable_cell = row.find("td", class_="clickable-row")
        if not clickable_cell:
            return None

        link = clickable_cell.find("a")
        if not link:
            return None

        song_name = link.get_text(strip=True)
        href = link.get("href")
        if not href:
            return None

        page_url = urljoin(str(base_url), href)
        return {
            "track_number": track_number,
            "song_name": song_name,
            "page_url": page_url
        }

    def _extract_track_number(self, cells) -> str | None:
        for cell in cells:
            text = cell.get_text(strip=True)
            if text.endswith(".") and text[:-1].isdigit():
                return text[:-1]
        return None

    async def _process_song_entry(self, entry: dict) -> File | None:
        try:
            html_content = await self._fetch_page(entry["page_url"])
        except Exception as e:
            print(f"Warning: Failed to fetch {entry['page_url']}: {e}")
            return None

        soup = BeautifulSoup(html_content, "html.parser")
        download_url, file_format = self._find_best_download_link(soup)

        if not download_url:
            print(f"Warning: No download link found for {entry['song_name']}")
            return None

        filename = f"{entry['track_number']}. {entry['song_name']}.{file_format}"
        return File(name=filename, url=HttpUrl(download_url))

    def _find_best_download_link(self, soup: BeautifulSoup) -> tuple[str | None, str | None]:
        download_spans = soup.find_all("span", class_="songDownloadLink")

        best_url = None
        best_format = None
        best_priority = -1

        for span in download_spans:
            parent_a = span.find_parent("a")
            if not parent_a:
                continue

            href = parent_a.get("href")
            if not href:
                continue

            for fmt in self.FORMAT_PRIORITY:
                if href.lower().endswith(f".{fmt}"):
                    priority = self.FORMAT_PRIORITY.index(fmt)
                    if priority > best_priority:
                        best_priority = priority
                        best_url = href
                        best_format = fmt
                    break

        return best_url, best_format
