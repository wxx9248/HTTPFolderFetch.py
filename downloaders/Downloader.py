from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from entities import Folder


class Downloader(ABC):
    @abstractmethod
    async def download(self, output_path: Union[str, Path], root: Folder) -> None:
        pass
