# Changelog

## v0.1.4 (2026-06-06)

- **Fixed:** Redirected URLs now recorded in `llms.txt` by their final URL instead of the original pre-redirect URL
- **Fixed:** Link extraction uses the page's final URL as base for resolving relative links after redirects

## v0.1.3 (2026-06-06)

- **Fixed:** Duplicate page entries in `llms.txt` caused by trailing-slash variants and `http`/`https` scheme variants - URLs are now normalized before deduplication

## v0.1.2 (2026-06-06)

- **Fixed:** `USER_AGENT` now reads from `__version__` - stays in sync automatically
- **Fixed:** `X-Robots-Tag: nofollow` is now respected - header-level and meta-level directives are merged
- **Fixed:** Playwright browser instance properly cleaned up on launch failure (resource leak)
- **Fixed:** `requests.Session` is now explicitly closed after crawl

## v0.1.1 (2026-06-06)

- **Fixed:** robots.txt returning 403/blocked no longer kills the entire crawl - gracefully falls back to allow-all
- **Fixed:** `--full` flag now generates separate `llms.txt` (summary) and `llms-full.txt` (full content) as specified
- **Fixed:** URL fragment stripping no longer corrupts paths (`str.rstrip` -> proper split)
- **Fixed:** `<h1>` text no longer overrides URL-path-based section grouping
- **Fixed:** Playwright fallback no longer triggered on 404/500 errors - only on empty JS-rendered content
- **Optimized:** Playwright browser instance reused across all JS fallback fetches (was launching/closing per-page)
- **Optimized:** HTML parsed once per page instead of three times (directives, metadata, link extraction)
- **Fixed:** `requirements.txt` no longer forces Playwright install (matches `pyproject.toml` optional-dep spec)
- **Removed:** Dead `isinstance(href, (list, tuple))` branch and unused regex

## v0.1.0 (2026-06-06)

- Initial release
