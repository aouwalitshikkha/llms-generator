# llms-generator

<p align="center">
  <a href="https://pypi.org/project/llms-generator/"><img src="https://img.shields.io/pypi/v/llms-generator" alt="PyPI"></a>
  <a href="https://pypi.org/project/llms-generator/"><img src="https://img.shields.io/pypi/pyversions/llms-generator" alt="Python Versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/llms-generator" alt="License"></a>
  <a href="https://github.com/aouwalitshikkha/llms-generator"><img src="https://img.shields.io/github/stars/aouwalitshikkha/llms-generator" alt="GitHub Stars"></a>
</p>

**Crawl any website and generate `llms.txt`** — the AI-ready site map standard.

`llms.txt` is a markdown file placed at a website's root (`/llms.txt`) that helps AI assistants like ChatGPT, Claude, and Perplexity understand your site's content structure. Think of it as *robots.txt for AI*.

This tool crawls your site, extracts page metadata, groups pages into logical sections, and outputs a spec-compliant `llms.txt` file.

---

## Why llms.txt?

AI systems struggle to navigate large, noisy websites. An `llms.txt` file gives them a curated map of your most important content — leading to:

-   Accurate citations in AI-generated responses
-   Better brand representation in ChatGPT, Perplexity, Google AI Overviews
-   Less server load from AI crawlers wandering your site
-   Control over how AI systems reference your content

The [llms.txt specification](https://llmstxt.org) was proposed by Jeremy Howard in 2024 and is actively supported by Perplexity, Anthropic, and other AI platforms.

---

## Installation

```bash
pip install llms-generator
```

For JavaScript-heavy sites (optional):

```bash
pip install llms-generator[js]
playwright install chromium
```

---

## Usage

```bash
llms-gen https://example.com
```

That's it. The tool crawls your site and creates `llms.txt` in the current directory.

### Options

| Flag | Default | Description |
|---|---|---|
| `URL` | required | Target website URL |
| `--depth` | `2` | Maximum crawl depth |
| `--output` | `llms.txt` | Output file path |
| `--full` | `False` | Also generate `llms-full.txt` with full page content |
| `--no-js` | `False` | Skip Playwright JavaScript rendering fallback |
| `--delay` | `1.0` | Seconds between requests (be polite) |

### Examples

```bash
# Basic crawl (2 levels deep)
llms-gen https://example.com

# Crawl deeper, output to custom path
llms-gen https://docs.example.com --depth 3 --output site-llms.txt

# Generate both standard and full versions
llms-gen https://example.com --full

# Fast crawl without JS rendering
llms-gen https://example.com --no-js --delay 0.5
```

---

## How it works

### Per-page robot check

Every page is checked against three layers before being included or followed:

```
robots.txt ──┬── disallowed? → skip
             └── allowed? ──→ check HTTP X-Robots-Tag header
                                     │
                           noindex? ──→ skip
                           nofollow? ──→ still analyze, don't follow links
                                     │
                           absent ──→ check <meta name="robots">
                                     │
                           noindex? ──→ skip
                           nofollow? ──→ still analyze, don't follow links
                                     │
                           absent/index,follow ──→ analyze + follow links
```

Pages with `noindex` are **excluded from `llms.txt`**. Pages with `nofollow` are still analyzed for their content but their child links are not crawled.

### Crawl strategy

1. Parse `robots.txt` — respect `Disallow` and `Crawl-Delay` (gracefully handles missing or restricted robots.txt)
2. BFS from the start URL up to `--depth` levels
3. For each page:
    - Fetch with `requests` (handles most sites)
    - Skip 4xx/5xx responses, non-HTML content, and `X-Robots-Tag: noindex`
    - If content is empty (JS-rendered), fall back to Playwright headless browser
    - Extract: `<title>`, `<h1>`, `<meta name="description">`, first meaningful paragraph, directory path
    - Check `<meta name="robots">` — `noindex` excludes the page, `nofollow` prevents link crawling
4. Group pages into sections (directory-based, with H1 fallback)
5. Assemble `llms.txt` per the spec

> **Performance note:** Playwright browser is launched once and reused across all JS fallback fetches, then cleaned up when the crawl completes.

### Section grouping

Pages are grouped into `##` sections by their top-level directory path:

```
/docs/getting-started   → ## Docs
/blog/hello-world       → ## Blog
/api/v1/users           → ## Api
```

Pages without a clear directory path use their `<h1>` as the section name.

---

## Output format

The generated `llms.txt` follows the [llmstxt.org](https://llmstxt.org) specification:

```markdown
# Example Site

> A great example site with documentation and blog content.

This file provides AI systems with a structured summary of this website.

## Docs

- [Getting Started](https://example.com/docs/getting-started): How to get started with our platform.
- [API Reference](https://example.com/docs/api): Complete API documentation.

## Blog

- [Hello World](https://example.com/blog/hello): Our first blog post.
```

### llms-full.txt

With `--full`, an expanded version is also generated that includes the full text content of each page inline — useful for providing complete context to LLMs in a single file.

---

## Changelog


### v0.1.3 (2026-06-06)

- **Fixed:** Duplicate page entries in llms.txt caused by trailing-slash variants and http/https scheme variants - URLs are now normalized before deduplication
### v0.1.2 (2026-06-06)

- **Fixed:** `USER_AGENT` now reads from `__version__` — stays in sync automatically
- **Fixed:** `X-Robots-Tag: nofollow` is now respected — header-level and meta-level directives are merged
- **Fixed:** Playwright browser instance properly cleaned up on launch failure (resource leak)
- **Fixed:** `requests.Session` is now explicitly closed after crawl

### v0.1.1 (2026-06-06)

- **Fixed:** robots.txt returning 403/blocked no longer kills the entire crawl — gracefully falls back to allow-all
- **Fixed:** `--full` flag now generates separate `llms.txt` (summary) and `llms-full.txt` (full content) as specified
- **Fixed:** URL fragment stripping no longer corrupts paths (`str.rstrip` → proper split)
- **Fixed:** `<h1>` text no longer overrides URL-path-based section grouping
- **Fixed:** Playwright fallback no longer triggered on 404/500 errors — only on empty JS-rendered content
- **Optimized:** Playwright browser instance reused across all JS fallback fetches (was launching/closing per-page)
- **Optimized:** HTML parsed once per page instead of three times (directives, metadata, link extraction)
- **Fixed:** `requirements.txt` no longer forces Playwright install (matches `pyproject.toml` optional-dep spec)
- **Removed:** Dead `isinstance(href, (list, tuple))` branch and unused regex

## Development

```bash
git clone https://github.com/aouwalitshikkha/llms-generator.git
cd llms-generator
pip install -e .
pip install -e ".[js]"   # with Playwright support
```

Run tests:

```bash
pip install pytest
pytest
```

---

## License

MIT
