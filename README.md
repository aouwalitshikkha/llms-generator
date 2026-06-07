# llms-generator

<p align="center">
  <a href="https://pypi.org/project/llms-generator/"><img src="https://img.shields.io/pypi/v/llms-generator" alt="PyPI"></a>
  <a href="https://llms-generator.readthedocs.io/"><img src="https://img.shields.io/badge/docs-Read%20the%20Docs-blue" alt="Docs"></a>
  <a href="https://pypi.org/project/llms-generator/"><img src="https://img.shields.io/pypi/pyversions/llms-generator" alt="Python Versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/llms-generator" alt="License"></a>
</p>

Crawl any website and generate `llms.txt`. A Markdown file at your domain root that tells AI systems which pages to read.

**Homepage:** https://abdulaouwal.com/project/llms-generator/
**Documentation:** https://llms-generator.readthedocs.io/

---

## Why llms.txt?

ChatGPT, Claude, and Gemini have small context windows. They cannot read your entire website. `llms.txt` gives them your essential pages in one request.

The [llms.txt specification](https://llmstxt.org) was proposed by Jeremy Howard in September 2024. It works alongside `robots.txt` and `sitemap.xml`. Each serves a different purpose.

---

## Installation

```bash
pip install llms-generator
```

For JavaScript-heavy sites:

```bash
pip install llms-generator[js]
playwright install chromium
```

---

## Usage

```bash
llms-gen https://example.com
```

This creates `llms.txt` in your current folder. Add `--full` to also generate the full content version.

### Options

| Flag | Default | Description |
|---|---|---|
| `URL` | required | Target website URL |
| `--depth` | `2` | Maximum crawl depth |
| `--output` | `llms.txt` | Output file path |
| `--full` | `false` | Also generate `llms-full.txt` |
| `--no-js` | `false` | Skip Playwright JS fallback |
| `--delay` | `1.0` | Seconds between requests |

### Examples

```bash
llms-gen https://example.com
llms-gen https://example.com --depth 3 --output site-llms.txt
llms-gen https://example.com --full
llms-gen https://example.com --no-js --delay 0.5
```

---

## How it works

### Robot checks

Every page passes three checks:

1. **robots.txt** - skips disallowed paths
2. **X-Robots-Tag** - respects `noindex` and `nofollow` from HTTP headers
3. **`<meta name="robots">`** - respects page-level directives

Pages marked `noindex` are excluded. Pages marked `nofollow` are analyzed but their links are not crawled.

### Crawl steps

1. Parse `robots.txt`. Handles missing or restricted files.
2. BFS from the start URL up to `--depth` levels.
3. For each page:
   - Fetch with `requests`
   - Skip 4xx/5xx responses and non-HTML content
   - Fall back to Playwright if content is empty (JS-rendered sites)
   - Extract title, h1, meta description, first paragraph, directory path
4. Group pages by top-level directory path
5. Write `llms.txt`

### Section grouping

```
/docs/getting-started   -> ## Docs
/blog/hello-world       -> ## Blog
/api/v1/users           -> ## Api
```

Pages without a directory path use their `<h1>` as the section name.

---

## Output

The generated `llms.txt` follows the [llmstxt.org](https://llmstxt.org) specification:

```markdown
# Example Site
> A great example site with documentation and blog content.

## Docs
- [Getting Started](https://example.com/docs/getting-started): How to get started.
- [API Reference](https://example.com/docs/api): Complete API documentation.

## Blog
- [Hello World](https://example.com/blog/hello): Our first blog post.
```

With `--full`, the tool also writes `llms-full.txt` with every page's full text under section headings.

---

## Contributing

1. Fork the repo and clone it
2. Create a branch: `git checkout -b my-change`
3. Install for development: `pip install -e .`
4. Run tests: `python -m pytest tests/`
5. Push and open a pull request

Keep PRs focused. One change per PR. Write a clear description of what you changed and why.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full release history.
