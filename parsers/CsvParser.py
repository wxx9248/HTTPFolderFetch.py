import csv
from pathlib import Path
from typing import List, Union

from entities import Downloadable
from parsers.Parser import Parser


class CsvParser(Parser):
    async def parse(self, file_path: Union[str, Path]) -> List[Downloadable]:
        downloadables = []
        path = file_path if isinstance(file_path, Path) else Path(file_path)
        
        # Use standard library to read CSV file
        with path.open("r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)

            # Skip header row if it exists
            # Assuming first row might be headers
            first_row = next(csv_reader, None)

            # Check if first row is a header row (contains "url" and "strategy")
            is_header = False
            if first_row and (first_row[0].lower() == "url" and
                              first_row[1].lower() == "strategy"):
                is_header = True

            # If first row is not a header, process it
            if not is_header and first_row:
                if len(first_row) >= 2:
                    downloadables.append(Downloadable(
                        url=first_row[0],
                        strategy=first_row[1]
                    ))

            # Process remaining rows
            for row in csv_reader:
                if len(row) >= 2:
                    downloadables.append(Downloadable(
                        url=row[0],
                        strategy=row[1]
                    ))

        return downloadables
