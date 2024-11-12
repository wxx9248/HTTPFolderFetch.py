import json
from pathlib import Path
from typing import List, Union

from entities import Downloadable
from parsers.Parser import Parser


class JsonParser(Parser):
    async def parse(self, file_path: Union[str, Path]) -> List[Downloadable]:
        path = file_path if isinstance(file_path, Path) else Path(file_path)
        with path.open("r") as f:
            data = json.load(f)
            return [Downloadable(**item) for item in data]
