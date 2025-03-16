from pathlib import Path
from typing import Union

import aiofiles

from downloaders.Downloader import Downloader
from entities import Folder


class Aria2Downloader(Downloader):
    def __init__(self, list_filename: Union[str, Path] = "aria2.list"):
        self.list_filename = Path(list_filename)

    async def download(self, output_path: Union[str, Path], root: Folder) -> None:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / self.list_filename

        async with aiofiles.open(file_path, "a") as f:
            await self._write_entries(f, root, output_path)

    async def _write_entries(self, f, folder: Folder, base_path: Path) -> None:
        current_path = base_path / folder.name

        for file in folder.files:
            relative_path = Path(folder.name) / file.name
            await f.write(f"{file.url}\n")
            await f.write(f"  dir={current_path}\n")
            await f.write(f"  out={file.name}\n\n")

        for subfolder in folder.folders:
            await self._write_entries(f, subfolder, current_path)
