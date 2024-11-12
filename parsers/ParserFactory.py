from pathlib import Path
from typing import Dict, Type, Union

from parsers.CsvParser import CsvParser
from parsers.JsonParser import JsonParser
from parsers.Parser import Parser


class ParserFactory:
    _parsers: Dict[str, Type[Parser]] = {
        ".json": JsonParser,
        ".csv": CsvParser,
    }

    @classmethod
    def create(cls, file_path: Union[str, Path]) -> Parser:
        path = file_path if isinstance(file_path, Path) else Path(file_path)
        file_ext = path.suffix.lower()

        if file_ext not in cls._parsers:
            raise ValueError(f"Unsupported file type: {file_ext}")

        return cls._parsers[file_ext]()
