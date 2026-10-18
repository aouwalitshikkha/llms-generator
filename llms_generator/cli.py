from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from llms_generator._version import __version__
from llms_generator.crawler import Crawler
from llms_generator.generator import generate_llms_txt
from llms_generator.section_grouper import group_pages
from llms_generator.validate import validate_llms_txt

log = logging.getLogger("llms_generator")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="llms-gen",
        description="Crawl a website and generate llms.txt",
    )
    parser.add_argument("url", help="Target website URL")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum crawl depth (default: 2)",
    )
    parser.add_argument(
        "--output",
        default="llms.txt",
        help="Output file path (default: llms.txt)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also generate llms-full.txt with full page content",
    )
    parser.add_argument(
        "--no-js",
        action="store_true",
        help="Skip Playwright JavaScript rendering fallback",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Base seconds between requests; adapts based on response time (default: 1.0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Stop after this many pages (0 = unlimited)",
    )
    parser.add_argument(
        "--prefer-markdown",
        action="store_true",
        help="Link to each page's markdown alternate when advertised",
    )
    parser.add_argument(
        "--optional-paths",
        default="",
        help="Comma-separated extra path names to move into the ## Optional section",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the generated llms.txt against the spec and exit non-zero on problems",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def full_output_path(output: str) -> Path:
    return Path(output).with_stem("llms-full")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    _configure_logging(args.verbose)

    crawler = Crawler(
        start_url=args.url,
        max_depth=args.depth,
        delay=args.delay,
        use_js=not args.no_js,
        timeout=args.timeout,
        max_pages=args.max_pages,
        prefer_markdown=args.prefer_markdown,
    )
    pages = crawler.run()

    if not pages:
        log.error("No pages found. Check the URL and try again.")
        sys.exit(1)

    optional_sections = [p.strip() for p in args.optional_paths.split(",") if p.strip()]
    sections = group_pages(pages, optional_sections=optional_sections)

    output = generate_llms_txt(sections, full=False)
    Path(args.output).write_text(output, encoding="utf-8")
    log.info(
        "Wrote %s with %d pages across %d sections.",
        args.output,
        len(pages),
        len(sections),
    )

    if args.full:
        full_output = generate_llms_txt(sections, full=True)
        full_path = full_output_path(args.output)
        full_path.write_text(full_output, encoding="utf-8")
        log.info("Wrote %s.", full_path)

    if args.check:
        problems = validate_llms_txt(output)
        if problems:
            for problem in problems:
                log.error("Validation: %s", problem)
            sys.exit(1)
        log.info("Validation passed.")


if __name__ == "__main__":
    main()
