# Things To Do - llms-generator

## Completed

- [x] `h1_tag` and `p_tag` guarded with `isinstance(tag, Tag)` before `.get_text()`
- [x] Adaptive rate limiting with jitter (`crawler.py:_adaptive_sleep`)
- [x] Removed `PageInfo.raw_html` — stored but never used
- [x] Created `AGENTS.md` with commands, layout, publishing flow, gotchas, dependencies

## High Priority

- [ ] **Remove duplicate section-inference logic** - `page_analyzer.py:_infer_section` and `section_grouper.py:_assign_section` duplicate each other
- [ ] **Fix `full_text` extraction quality** - Prefer `<article>`, `<main>`, `[role="main"]` over `<div>`/`<section>`
- [ ] **Add crawler/CLI tests** - BFS, robots.txt, Playwright fallback, CLI args are uncovered
- [ ] **Add `logging`** - Replace `print()` with `logging` for debug-level crawl progress
- [ ] **Add configurable `--timeout`** - 30s hardcoded in `crawler.py`
- [ ] **Fix `full_path` logic** - Use `Path(args.output).with_stem("llms-full")` instead of `.replace()`

## Medium Priority

- [ ] **Add `py.typed` marker file** - Declared in `package-data` but file doesn't exist
- [ ] **Playwright context manager** - Use `with sync_playwright() as pw:` instead of manual `__exit__`
- [ ] **Normalize default ports** - `_url_key` doesn't strip `:80` / `:443`
- [ ] **Omit redundant `: desc` in generator output** - Skip `: desc` when it equals the link text
- [ ] **Add tool config to `pyproject.toml`** - pytest, ruff, mypy configs

## Low Priority

- [ ] **Remove `PageInfo.raw_html`** - Stored but never used
- [ ] **`cli.py` missing `from __future__ import annotations`** - Inconsistent with other modules
- [ ] **Expose public API** - Export `crawl()`, `generate()`, `PageInfo` from `__init__.py`
- [ ] **No warning when pages silently skipped** - Empty/non-HTML/noindex pages all skipped silently
- [ ] **No sitemap.xml discovery** - `robots.txt` `Sitemap:` directive ignored
- [ ] **Consider `setuptools-scm`** - Replace hardcoded `_version.py` with git tag versioning
