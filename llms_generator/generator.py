from __future__ import annotations

from urllib.parse import urlparse

from llms_generator.page_analyzer import PageInfo


def generate_llms_txt(
    sections: dict[str, list[PageInfo]],
    full: bool = False,
) -> str:
    lines: list[str] = []

    # H1 — site name from the start URL's netloc
    site_name = _pick_site_name(sections)
    lines.append(f"# {site_name}")
    lines.append("")

    # Blockquote summary — first non-empty description
    summary = _pick_summary(sections)
    if summary:
        lines.append(f"> {summary}")
        lines.append("")

    # Optional context paragraph
    lines.append(
        "This file provides AI systems with a structured summary of this website. "
        "It is maintained automatically by llms-generator."
    )
    lines.append("")

    # Sections
    for section_name in _order_sections(sections):
        pages = sections[section_name]
        if not pages:
            continue

        lines.append(f"## {section_name}")
        lines.append("")

        for page in pages:
            desc = page.summary or page.h1 or page.title
            lines.append(f"- [{page.title or page.h1 or page.url}]({page.url}): {desc}")

            if full and page.full_text:
                lines.append("")
                lines.append(page.full_text)
                lines.append("")

        lines.append("")

    return "\n".join(lines)


def _pick_site_name(sections: dict[str, list[PageInfo]]) -> str:
    for pages in sections.values():
        for p in pages:
            if p.title:
                return p.title.split("—")[0].split("|")[0].strip()
            if p.h1:
                return p.h1
    # Fallback: domain name
    for pages in sections.values():
        for p in pages:
            netloc = urlparse(p.url).netloc
            return netloc.replace("www.", "").split(".")[0].title()
    return "Untitled Site"


def _pick_summary(sections: dict[str, list[PageInfo]]) -> str:
    for name in ("Home", "About", "Docs"):
        pages = sections.get(name)
        if pages:
            for p in pages:
                if p.description:
                    return p.description
                if p.summary:
                    return p.summary
    # Fallback: any non-empty summary
    for pages in sections.values():
        for p in pages:
            if p.description:
                return p.description
    return ""


SECTION_PRIORITY = [
    "Home", "About", "Docs", "Documentation",
    "Guide", "Guides", "Tutorial", "Tutorials",
    "Api", "Api Reference",
    "Blog", "News",
    "Features", "Pricing",
    "Support", "Faq",
    "Contact",
]


def _order_sections(sections: dict[str, list[PageInfo]]) -> list[str]:
    custom: list[str] = []
    remaining: list[str] = []

    for name in sections:
        if name in SECTION_PRIORITY:
            custom.append(name)
        else:
            remaining.append(name)

    custom.sort(key=lambda n: SECTION_PRIORITY.index(n))
    remaining.sort()

    return custom + remaining
