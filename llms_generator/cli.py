import argparse
import sys

from llms_generator.crawler import Crawler
from llms_generator.section_grouper import group_pages
from llms_generator.generator import generate_llms_txt


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="llms-gen",
        description="Crawl a website and generate llms.txt",
    )
    parser.add_argument("url", help="Target website URL")
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    crawler = Crawler(
        start_url=args.url,
        max_depth=args.depth,
        delay=args.delay,
        use_js=not args.no_js,
    )
    pages = crawler.run()

    if not pages:
        print("No pages found. Check the URL and try again.", file=sys.stderr)
        sys.exit(1)

    sections = group_pages(pages)

    output = generate_llms_txt(sections, full=False)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Wrote {args.output} with {len(pages)} pages across {len(sections)} sections.")

    if args.full:
        full_output = generate_llms_txt(sections, full=True)
        full_path = args.output.replace("llms.txt", "llms-full.txt")
        if full_path == args.output:
            full_path = "llms-full.txt"
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_output)
        print(f"Wrote {full_path}.")


if __name__ == "__main__":
    main()
