# Changelog

## v0.3.0 (2026-10-18)

- **Added:** `## Optional` section support — secondary pages (privacy, terms, cookies, legal, tags, authors, archives, etc.) are grouped into a trailing `## Optional` section per the llms.txt spec. Add more via `--optional-paths`.
- **Added:** `--prefer-markdown` — link to a page's markdown alternate (`rel="alternate" type="text/markdown"`) when advertised.
- **Added:** `--check` — validate the generated `llms.txt` against the spec and exit non-zero on problems.
- **Added:** `--timeout` and `--max-pages` options.
- **Added:** `--version` and `-v/--verbose` flags; crawl progress is now reported through `logging`.
- **Added:** `llms_generator.validate.validate_llms_txt()` for programmatic validation.
- **Added:** public API exports (`Crawler`, `PageInfo`, `generate_llms_txt`, `group_pages`, `validate_llms_txt`) from `llms_generator`.
- **Added:** `py.typed` marker; project now ships type information.
- **Added:** CI workflow (Python 3.10–3.13: ruff + pytest). Publishing consolidated to a single OIDC (trusted publishing) workflow triggered by `v*` tags.
- **Changed:** Improved `--full` text extraction — prefers `<article>`, `<main>`, `[role="main"]` and strips nav/header/footer/aside/script boilerplate.
- **Changed:** Site name now prefers `og:site_name`.
- **Changed:** Redundant `: description` notes are omitted when they duplicate the link text.
- **Changed:** Tracking query parameters (`utm_*`, `fbclid`, `gclid`, `ref`, …) are stripped and remaining params sorted, preventing duplicate crawls.
- **Changed:** Default ports (`:80`/`:443`) are normalized.
- **Fixed:** Per-link `rel="nofollow"`, `rel="ugc"`, and `rel="sponsored"` links are no longer followed.
- **Fixed:** Off-domain redirects no longer add foreign pages.
- **Fixed:** Transient failures (429/5xx/timeouts) are retried with `Retry-After` backoff.
- **Fixed:** Pages are fetched even when the server omits a `Content-Type` header (body sniffing), and character encoding falls back to `apparent_encoding`.
- **Fixed:** `robots.txt` is respected via a fixed `llms-generator` user-agent token; `crawl-delay` is honored.
- **Fixed:** `--full` output path uses `Path.with_stem` instead of a fragile string `replace`.
- **Removed:** Duplicate section-inference logic (now owned by `section_grouper`); token-based `publish.yml` workflow.

## v0.2.1 (2026-06-12)

- **Removed:** `PageInfo.raw_html` field — stored but never read

## v0.2.0 (2026-06-12)

- **Added:** Adaptive rate limiting — delay now adjusts based on server response time with random jitter to avoid pattern detection
- **Changed:** `--delay` is now a base minimum; actual wait time scales up when the server responds slowly

## v0.1.11 (2026-06-12)

- **Fixed:** `h1_tag` and `p_tag` now guarded with `isinstance(tag, Tag)` to prevent `AttributeError` from `NavigableString` matches in `page_analyzer.py`

## v0.1.10 (2026-06-07)

- **Fixed:** `Development Status` classifier set to `4 - Beta` (was `3 - Alpha`)

## v0.1.9 (2026-06-07)

- **Added:** Project homepage link to `pyproject.toml` and `README.md` — https://abdulaouwal.com/project/llms-generator/
- **Changed:** Bumped version from 0.1.8 to 0.1.9

## v0.1.7 (2026-06-06)

(This release was published directly to PyPI without a formal changelog entry.)

## v0.1.6 (2026-06-06)

- **Updated:** README cleaned up. Removed em dashes and AI-sounding phrases. Added Read the Docs badge and documentation link.

## v0.1.5 (2026-06-06)

- **Added:** Changelog URL in pyproject.toml so the changelog link appears on PyPI

## v0.1.4 (2026-06-06)

- **Fixed:** Redirected URLs now recorded in `llms.txt` by their final URL instead of the original pre-redirect URL
- **Fixed:** Link extraction uses the page's final URL as base for resolving relative links after redirects

## v0.1.3 (2026-06-06)

- **Fixed:** Duplicate page entries in `llms.txt` caused by trailing-slash variants and `http`/`https` scheme variants. URLs are now normalized before deduplication.

## v0.1.2 (2026-06-06)

- **Fixed:** `USER_AGENT` now reads from `__version__`. Stays in sync automatically.
- **Fixed:** `X-Robots-Tag: nofollow` is now respected. Header-level and meta-level directives are merged.
- **Fixed:** Playwright browser instance properly cleaned up on launch failure (resource leak)
- **Fixed:** `requests.Session` is now explicitly closed after crawl

## v0.1.1 (2026-06-06)

- **Fixed:** robots.txt returning 403/blocked no longer kills the entire crawl. Gracefully falls back to allow-all.
- **Fixed:** `--full` flag now generates separate `llms.txt` (summary) and `llms-full.txt` (full content) as specified
- **Fixed:** URL fragment stripping no longer corrupts paths (`str.rstrip` replaced with proper split)
- **Fixed:** `<h1>` text no longer overrides URL-path-based section grouping
- **Fixed:** Playwright fallback no longer triggered on 404/500 errors. Only on empty JS-rendered content.
- **Optimized:** Playwright browser instance reused across all JS fallback fetches
- **Optimized:** HTML parsed once per page instead of three times
- **Fixed:** `requirements.txt` no longer forces Playwright install
- **Removed:** Dead `isinstance(href, (list, tuple))` branch and unused regex

## v0.1.0 (2026-06-06)

- Initial release
