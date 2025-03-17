import uvloop
import asyncio
import sys
from pathlib import Path

from downloaders import DownloaderFactory
from entities import Downloadable
from parsers import ParserFactory
from strategies import StrategyFactory


async def process_downloadable(downloadable: Downloadable, output_path: Path) -> None:
    strategy = StrategyFactory.create(downloadable.strategy)
    root = await strategy.execute(str(downloadable.url))
    downloader = DownloaderFactory.create()
    await downloader.download(output_path, root)


async def main():
    # Default output directory
    default_output_dir = Path("Downloaded")

    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_directory]")
        print(f"If output_directory is not specified, '{default_output_dir}' will be used")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    # Use specified output directory or default
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else default_output_dir

    parser = ParserFactory.create(input_file)
    downloadables = await parser.parse(input_file)

    tasks = [process_downloadable(d, output_dir) for d in downloadables]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    
  uvloop.run(main())
  # asyncio.run(main())
