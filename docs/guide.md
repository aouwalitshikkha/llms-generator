# Guide

## Quickstart

You need Python 3.10 or newer installed.

```bash
pip install llms-generator
llms-gen https://example.com
```

This creates `llms.txt` in your current folder. Add `--full` to also generate the full content version:

```bash
llms-gen https://example.com --full
```

## Usage

### Crawl options

| Flag | Default | Description |
|------|---------|-------------|
| `URL` | required | Target website URL |
| `--depth` | 2 | Maximum crawl depth |
| `--output` | llms.txt | Output file path |
| `--full` | false | Also generate llms-full.txt |
| `--delay` | 1.0 | Base seconds between requests (adapts to response time) |
| `--timeout` | 30 | Per-request timeout in seconds |
| `--max-pages` | 0 | Stop after this many pages (0 = unlimited) |
| `--prefer-markdown` | false | Link to each page's markdown alternate when advertised |
| `--optional-paths` | none | Extra path names to move into `## Optional` |
| `--check` | false | Validate the output against the spec |
| `-v`, `--verbose` | false | Enable debug logging |
| `--no-js` | false | Skip Playwright JS fallback |

### Examples

Crawl with custom depth and delay:

```bash
llms-gen https://example.com --depth 3 --delay 0.5
```

Write to a specific output path:

```bash
llms-gen https://example.com --output public/llms.txt
```

Validate the output and cap the crawl:

```bash
llms-gen https://example.com --check --max-pages 100 --timeout 15
```

### Optional section

Secondary pages (privacy, terms, cookies, legal, tags, authors, archives, …) are grouped into a trailing `## Optional` section. Add your own with a comma-separated list:

```bash
llms-gen https://example.com --optional-paths changelog,careers
```

### JavaScript sites

Install with JS support:

```bash
pip install llms-generator[js]
```

The tool falls back to Playwright when HTTP fetch returns empty content.

### Excluding paths

Add Disallow rules in `robots.txt`:

```
User-agent: llms-generator/0.1
Disallow: /tag/
Disallow: /author/
```
