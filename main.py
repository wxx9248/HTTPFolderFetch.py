import asyncio
import sys
from pathlib import Path

import uvloop

from downloaders import DownloaderFactory
from entities import Crawlable
from parsers import ParserFactory
from strategies import StrategyFactory


async def process_crawlable(crawlable: Crawlable, output_path: Path) -> None:
    strategy = StrategyFactory.create(crawlable.strategy)
    folder = await strategy.execute(crawlable.url)
    downloader = DownloaderFactory.create()
    await downloader.download(output_path, folder)


async def main():
    # Default output directory
    default_output_dir = Path("Downloaded")

    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_directory]")
        print(
            f"If output_directory is not specified, '{default_output_dir}' will be used"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])

    # Use specified output directory or default
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else default_output_dir

    parser = ParserFactory.create(input_file)
    crawlables = await parser.parse(input_file)

    await asyncio.gather(*[process_crawlable(c, output_dir) for c in crawlables])


if __name__ == "__main__":
    uvloop.run(main())
