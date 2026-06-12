# Changelog

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
