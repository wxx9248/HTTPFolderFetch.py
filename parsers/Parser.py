from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from entities import Crawlable


class Parser(ABC):
    @abstractmethod
    async def parse(self, file_path: Union[str, Path]) -> List[Crawlable]:
        pass
