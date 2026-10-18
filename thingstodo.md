# Things To Do - llms-generator

## Completed (v0.3.0)

- [x] `h1_tag` and `p_tag` guarded with `isinstance(tag, Tag)` before `.get_text()`
- [x] Adaptive rate limiting with jitter (`crawler.py:_adaptive_sleep`)
- [x] Removed `PageInfo.raw_html` — stored but never used
- [x] Created `AGENTS.md` with commands, layout, publishing flow, gotchas, dependencies
- [x] Removed duplicate section-inference logic — single owner in `section_grouper.py`
- [x] Fixed `full_text` extraction — prefers `<article>`, `<main>`, `[role="main"]`, strips boilerplate
- [x] Added crawler + CLI tests (offline via `responses`)
- [x] Replaced `print()` with `logging` (+ `-v/--verbose`)
- [x] Added configurable `--timeout`
- [x] Fixed `full_path` logic — `Path.with_stem("llms-full")`
- [x] Added `py.typed` marker file
- [x] Playwright lifecycle via `sync_playwright().start()/stop()`
- [x] Normalized default ports (`:80` / `:443`)
- [x] Omit redundant `: desc` in generator output
- [x] Added tool config to `pyproject.toml` (pytest, ruff, mypy)
- [x] `cli.py` `from __future__ import annotations`
- [x] Exposed public API from `__init__.py`
- [x] Warn on `--max-pages` truncation; debug logs for skipped pages
- [x] Stripped tracking query params; retry/429 + `Retry-After`; per-link `rel=nofollow`; off-domain redirect guard
- [x] `## Optional` section, `--prefer-markdown`, `--check`/`validate_llms_txt`, `og:site_name`
- [x] CI workflow (ruff + pytest, Python 3.10–3.13); single OIDC publish workflow

## Remaining

- [ ] **sitemap.xml discovery** - `robots.txt` `Sitemap:` directive is still ignored
- [ ] **Concurrency** - crawl is serial; consider a small polite thread pool
- [ ] **`setuptools-scm`** - Replace hardcoded `_version.py` with git tag versioning
- [ ] **Sitemap-based seeds** - use sitemap URLs as additional starting points
- [ ] **Config file** - support `.llmsgen.toml` / `pyproject.toml` options
