from typing import Dict, Type

from downloaders.Aria2Downloader import Aria2Downloader
from downloaders.Downloader import Downloader


class DownloaderFactory:
    # Dictionary mapping downloader names to their classes
    _downloaders: Dict[str, Type[Downloader]] = {
        "aria2": Aria2Downloader,
    }

    @classmethod
    def create(cls, downloader_type: str = "aria2") -> Downloader:
        if downloader_type not in cls._downloaders:
            raise ValueError(f"Unsupported downloader type: {downloader_type}")

        return cls._downloaders[downloader_type]()
