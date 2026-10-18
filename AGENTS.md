# llms-generator - Agent Guide

## Commands

```
pip install -e ".[dev]"                       # dev install (pytest, ruff, mypy, responses)
pytest tests/ -q                              # run all tests
ruff check .                                  # lint
mypy llms_generator                           # type-check
```

## Project layout

- `llms_generator/` - package
  - `cli.py` - argparse entrypoint (`llms-gen` / `python -m llms_generator`)
  - `crawler.py` - BFS crawler with robots.txt, requests, optional Playwright, adaptive rate limiting
  - `page_analyzer.py` - PageInfo dataclass, meta/robots parsing, content extraction
  - `section_grouper.py` - groups pages by URL path segment; sole owner of section inference + Optional classification
  - `generator.py` - renders llms.txt output
  - `validate.py` - `validate_llms_txt()` spec checker (used by `--check`)
  - `_version.py` - source of version; also update docs/conf.py release on bump
- `tests/` - pytest (offline, uses `responses` for the crawler)

## Publishing

Single GitHub Actions workflow on tag push `v*`:

- **release.yml** - builds and publishes to PyPI via OIDC trusted publishing (no API token). Requires a PyPI trusted publisher for workflow `release.yml`.

- **ci.yml** - runs ruff + pytest on push to `main` and on PRs (Python 3.10–3.13).

Release flow: bump `_version.py` -> docs/conf.py `release` -> CHANGELOG.md -> commit -> merge to main -> `git tag vX.Y.Z && git push origin main vX.Y.Z`.

## Gotchas

- Path `D:\Tools\_In_Progress\llms text generator` has underscores and parens - some tools break on it. Use `-LiteralPath` and `--git-dir`/`--work-tree` when needed.
- Section inference lives only in `section_grouper.py`; `page_analyzer.extract_page_info` no longer sets `PageInfo.section`.
- `h1_tag` and `p_tag` need `isinstance(tag, Tag)` guard before `.get_text()`.

## Dependencies

- Required: requests, beautifulsoup4
- Optional: playwright (JS rendering, `pip install llms-generator[js]`)
- Python >= 3.10, setuptools build
