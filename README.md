# llms-generator

Crawl any website and generate `llms.txt` — the AI-ready site map standard.

## Quick start

```bash
pip install llms-generator

llms-gen https://example.com --depth 2
```

## Options

| Flag | Default | Description |
|---|---|---|
| `URL` | required | Target site URL |
| `--depth` | `2` | Max crawl depth |
| `--output` | `llms.txt` | Output file path |
| `--full` | `False` | Also generate `llms-full.txt` |
| `--no-js` | `False` | Skip Playwright JavaScript fallback |
| `--delay` | `1` | Seconds between requests |

## What it checks per page

- `robots.txt` — skip disallowed paths
- `X-Robots-Tag` HTTP header — respect `noindex` / `nofollow`
- `<meta name="robots">` — respect `noindex` / `nofollow`

Pages with `noindex` are excluded from output. Pages with `nofollow` are still analyzed but their links are not followed.

## Output format

Follows the [llms.txt](https://llmstxt.org) standard:

```markdown
# Site Name

> Brief description

## Docs
- [Page Title](https://...): Meta description or page summary.

## Blog
- [Post Title](https://...): ...
```
