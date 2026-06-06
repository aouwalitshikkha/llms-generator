# llms-generator

<p align="center">
  <a href="https://pypi.org/project/llms-generator/"><img src="https://img.shields.io/pypi/v/llms-generator" alt="PyPI"></a>
  <a href="https://llms-generator.readthedocs.io/"><img src="https://img.shields.io/badge/docs-Read%20the%20Docs-blue" alt="Docs"></a>
  <a href="https://pypi.org/project/llms-generator/"><img src="https://img.shields.io/pypi/pyversions/llms-generator" alt="Python Versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/llms-generator" alt="License"></a>
</p>

**Crawl any website and generate `llms.txt`** - the AI-ready site map standard.

`llms.txt` is a Markdown file placed at your domain root (`/llms.txt`) that provides a curated overview of your most important pages for AI systems. It is designed for inference time (when users ask questions), not for training.

This tool crawls your site, extracts page metadata, groups pages into logical sections, and outputs a spec-compliant `llms.txt` file.

**Documentation:** https://llms-generator.readthedocs.io/

---

## Why llms.txt?

ChatGPT, Claude, and Gemini have small context windows. They cannot read your entire website with navigation, JavaScript, and ads. `llms.txt` gives them your essential pages in one request.

- Accurate citations in AI-generated responses
- Better brand representation in ChatGPT, Perplexity, Google AI Overviews
- Less server load from AI crawlers wandering your site
- Control over how AI systems reference your content

The [llms.txt specification](https://llmstxt.org) was proposed by Jeremy Howard (AnswerDotAI, September 2024). It coexists with `robots.txt` and `sitemap.xml` - each serves a different purpose.

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

That creates `llms.txt` in the current folder. Add `--full` to also generate the full content version:

```bash
llms-gen https://example.com --full
```

### Options

| Flag | Default | Description |
|---|---|---|
| `URL` | required | Target website URL |
| `--depth` | `2` | Maximum crawl depth |
| `--output` | `llms.txt` | Output file path |
| `--full` | `false` | Also generate `llms-full.txt` with full page content |
| `--no-js` | `false` | Skip Playwright JavaScript rendering fallback |
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

Every page is checked against three layers before being included:

1. **robots.txt** - Skips disallowed paths automatically
2. **X-Robots-Tag** - Respects `noindex` and `nofollow` from HTTP headers
3. **`<meta name="robots">`** - Respects page-level directives in the HTML

Pages with `noindex` are excluded from `llms.txt`. Pages with `nofollow` are still analyzed but their links are not crawled.

### Crawl strategy

1. Parse `robots.txt` - respects `Disallow` and `Crawl-Delay` (gracefully handles missing or restricted robots.txt)
2. BFS from the start URL up to `--depth` levels
3. For each page:
   - Fetch with `requests` (handles most sites)
   - Skip 4xx/5xx responses, non-HTML content, and `X-Robots-Tag: noindex`
   - If content is empty (JS-rendered), fall back to Playwright headless browser
   - Extract: `<title>`, `<h1>`, `<meta name="description">`, first meaningful paragraph, directory path
   - Check `<meta name="robots">` - `noindex` excludes the page, `nofollow` prevents link crawling
4. Group pages into sections (directory-based, with H1 fallback)
5. Assemble `llms.txt` per the spec

> **Performance note:** Playwright browser is launched once and reused across all JS fallback fetches, then cleaned up when the crawl completes.

### Section grouping

Pages are grouped into `##` sections by their top-level directory path:

```
/docs/getting-started   -> ## Docs
/blog/hello-world       -> ## Blog
/api/v1/users           -> ## Api
```

Pages without a clear directory path use their `<h1>` as the section name.

---

## Output format

The generated `llms.txt` follows the [llmstxt.org](https://llmstxt.org) specification:

```markdown
# Example Site
> A great example site with documentation and blog content.

## Docs
- [Getting Started](https://example.com/docs/getting-started): How to get started with our platform.
- [API Reference](https://example.com/docs/api): Complete API documentation.

## Blog
- [Hello World](https://example.com/blog/hello): Our first blog post.
```

### llms-full.txt

With `--full`, an expanded version is also generated that includes the full text content of each page inline - useful for providing complete context to LLMs in a single file.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full release history.
