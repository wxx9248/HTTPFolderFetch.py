import argparse
import asyncio
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

    parser = argparse.ArgumentParser(
        prog="HTTPFolderFetch",
        description="A simple web folder crawler"
    )
    parser.add_argument("--output-dir", default=default_output_dir,
                        help=f"set output directory. If output_directory is not specified, '{default_output_dir}' will be used.")
    parser.add_argument("input",
                        help="a file containing URLs to crawl and their corresponding strategies. Supports CSV and JSON.")
    arguments = parser.parse_args()

    input_file = Path(arguments.input)

    # Use specified output directory or default
    output_dir = Path(arguments.output_dir) if arguments.output_dir else default_output_dir

    parser = ParserFactory.create(input_file)
    crawlables = await parser.parse(input_file)

    await asyncio.gather(*[process_crawlable(c, output_dir) for c in crawlables])


if __name__ == "__main__":
    uvloop.run(main())
