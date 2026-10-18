# llms-generator - Agent Guide

Crawl a website and generate `llms.txt` (the AI-ready site map standard at
<https://llmstxt.org>). Single package, no runtime services.

Author: **Abdul Aouwal**, Technical SEO Consultant (<https://abdulaouwal.com/>).
Use this canonical name/title in metadata, docs, and commit authorship.

## Commands

```
pip install -e ".[dev]"                       # dev install (pytest, ruff, mypy, responses)
pytest tests/ -q                              # run all tests (33)
pytest tests/test_crawler.py -q               # single file
ruff check .                                  # lint
ruff check . --fix                            # auto-fix lint
mypy llms_generator                           # type-check
python -m build                               # build sdist + wheel into dist/
llms-gen https://example.com --check          # CLI smoke test
```

## Project layout

- `llms_generator/` - package
  - `cli.py` - argparse entrypoint (`llms-gen` / `python -m llms_generator`);
    flags: `--depth --output --full --no-js --delay --timeout --max-pages
    --prefer-markdown --optional-paths --check -v/--verbose --version`.
    `full_output_path()` derives the `llms-full.txt` path.
  - `crawler.py` - BFS crawler. robots.txt (+ `crawl-delay`, fixed UA token
    `llms-generator`), tracker-param stripping, `--max-pages`, per-link
    `rel=nofollow|ugc|sponsored`, off-domain redirect guard, retry/`Retry-After`,
    content sniffing, `apparent_encoding`, optional Playwright fallback,
    adaptive rate limiting, port normalization.
  - `page_analyzer.py` - `PageInfo` + `RobotsDirectives` dataclasses; meta/robots
    parsing; `extract_page_info()` (title, h1, description, `og:site_name`,
    main-text). Does NOT set `PageInfo.section`.
  - `section_grouper.py` - `group_pages()`; sole owner of section inference and
    `## Optional` classification (default heuristic + `--optional-paths`).
  - `generator.py` - renders `llms.txt` / `llms-full.txt`; site name from
    `og:site_name`; `## Optional` ordered last; redundant `: desc` omitted.
  - `validate.py` - `validate_llms_txt()` spec checker (used by `--check`).
  - `__init__.py` - public API: `Crawler`, `PageInfo`, `generate_llms_txt`,
    `group_pages`, `validate_llms_txt`, `__version__`.
  - `py.typed` - ships type info (declared in `package-data`).
  - `_version.py` - source of version; also update `docs/conf.py` `release` on bump.
- `tests/` - pytest, fully offline. `test_crawler.py` uses `responses` and
  monkeypatches `Crawler._load_robots_txt` / `_adaptive_sleep`.
- `docs/` - Sphinx (myst) on Read the Docs; `docs/changelog.md` mirrors
  `CHANGELOG.md` (keep both in sync on release).

## Publishing

Two GitHub Actions workflows:

- **ci.yml** - ruff + pytest on push to `main` and on PRs (Python 3.10–3.13).
- **release.yml** - on tag push `v*`: builds and publishes to PyPI via OIDC
  trusted publishing (no API token; `attestations: true`). Requires a PyPI
  trusted publisher (owner `aouwalitshikkha`, repo `llms-generator`, workflow
  `release.yml`, no environment).

Release flow:
1. Bump `llms_generator/_version.py`, `docs/conf.py` `release`, `CHANGELOG.md`,
   `docs/changelog.md`.
2. Commit on a branch, run `pytest` / `ruff` / `mypy`, merge to `main`.
3. `git tag vX.Y.Z && git push origin main vX.Y.Z` (the tag triggers publish).
4. Check: `gh run list` / `gh run view <id> --log-failed`.

## Gotchas

- Path `D:\Tools\_In_Progress\llms text generator` has underscores and parens -
  some tools break on it. Use `-LiteralPath` and `--git-dir`/`--work-tree`.
- Shell is Windows PowerShell 5.1: no heredocs, no `&&`. Chain with
  `cmd1; if ($?) { cmd2 }`. For multi-line commit messages write a file and use
  `git commit -F <file>`.
- Section inference lives only in `section_grouper.py`;
  `page_analyzer.extract_page_info` leaves `PageInfo.section` empty.
- `h1_tag` / `p_tag` / `meta` tags need `isinstance(tag, Tag)` guards before
  `.get_text()` / attribute access; `Tag.get()` can return `str | list`.
- `_url_key` dedups on a normalized URL (scheme, ports, tracker params, trailing
  slash) — keep `_normalize_url` and `_extract_links` consistent with it.
- Playwright is optional; tests must not require it (use `use_js=False`).
- Never let a crawl hit the network in tests — always mock with `responses`.

## Dependencies

- Required: `requests`, `beautifulsoup4`
- Extras: `js` = playwright; `dev` = pytest, ruff, mypy, responses;
  `all` = `llms-generator[js]`
- Python >= 3.10, setuptools build (`[tool.setuptools.dynamic]` reads version
  from `_version.py`)
