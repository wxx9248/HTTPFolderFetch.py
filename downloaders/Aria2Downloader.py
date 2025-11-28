from pathlib import Path
from typing import Union

import aiofiles

from downloaders.Downloader import Downloader
from entities import Folder


class Aria2Downloader(Downloader):
    def __init__(self, list_filename: Union[str, Path] = "aria2.list"):
        self.list_filename = Path(list_filename)

    async def download(self, output_path: Union[str, Path], folder: Folder) -> None:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / self.list_filename

        async with aiofiles.open(file_path, "a") as f:
            await self._write_entries(f, folder, output_path)

    async def _write_entries(self, f, folder: Folder, base_path: Path) -> None:
        current_path = base_path / folder.name

        for file in folder.files:
            # Write all lines for one entry atomically to prevent interleaving
            entry = f"{file.url}\n  dir={current_path}\n  out={file.name}\n\n"
            await f.write(entry)

        for subfolder in folder.folders:
            await self._write_entries(f, subfolder, current_path)
