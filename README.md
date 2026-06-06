# llms-generator

[![PyPI](https://img.shields.io/pypi/v/llms-generator)](https://pypi.org/project/llms-generator/)
[![Python](https://img.shields.io/pypi/pyversions/llms-generator)](https://pypi.org/project/llms-generator/)
[![License](https://img.shields.io/github/license/aouwalitshikkha/llms-generator)](LICENSE)

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

1. Parse `robots.txt` — respect `Disallow` and `Crawl-Delay`
2. BFS from the start URL up to `--depth` levels
3. For each page:
    - Fetch with `requests` (handles most sites)
    - If content is empty (JS-rendered), fall back to Playwright headless browser
    - Extract: `<title>`, `<h1>`, `<meta name="description">`, first meaningful paragraph, directory path
4. Group pages into sections (directory-based, with H1 fallback)
5. Assemble `llms.txt` per the spec

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
