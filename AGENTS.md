# llms-generator - Agent Guide

## Commands

```
pytest tests/ -v                              # run all 9 tests
pytest tests/test_page_analyzer.py -v          # single file
```

## Project layout

- `llms_generator/` - package
  - `cli.py` - argparse entrypoint (`llms-gen` / `python -m llms_generator`)
  - `crawler.py` - BFS crawler with robots.txt, requests, optional Playwright, adaptive rate limiting
  - `page_analyzer.py` - PageInfo dataclass, meta/robots parsing, content extraction
  - `section_grouper.py` - groups pages by URL path segment
  - `generator.py` - renders llms.txt output
  - `_version.py` - source of version; also update docs/conf.py release on bump
- `tests/` - pytest (no crawler.py or cli.py tests yet)

## Publishing

Two GitHub Actions on tag push v*:

- **publish.yml** - builds and publishes to PyPI via PYPI_API_TOKEN secret (works)
- **release.yml** - triggered on GitHub Release publish, uses OIDC trusted publishing (fails since v0.1.1 - PyPI trusted publisher not configured for tag events)

Release flow: bump _version.py -> docs/conf.py -> CHANGELOG.md -> commit -> tag && push --tags -> gh release create

## Gotchas

- Path `D:\Tools\_In_Progress\llms text generator` has underscores and parens - some tools break on it. Use `-LiteralPath` and `--git-dir`/`--work-tree` when needed.
- `page_analyzer.py` section inference partially duplicates `section_grouper.py` - prefer the latter for grouping.
- `PageInfo.raw_html` stored but never read.
- `h1_tag` and `p_tag` need `isinstance(tag, Tag)` guard before `.get_text()`.

## Dependencies

- Required: requests, beautifulsoup4
- Optional: playwright (JS rendering, `pip install llms-generator[js]`)
- Python >= 3.10, setuptools build
