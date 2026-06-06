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
| `--delay` | 1.0 | Seconds between requests |
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
