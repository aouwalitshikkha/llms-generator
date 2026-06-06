from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlparse

from llms_generator.page_analyzer import PageInfo


def group_pages(pages: list[PageInfo]) -> dict[str, list[PageInfo]]:
    sections: dict[str, list[PageInfo]] = defaultdict(list)

    for page in pages:
        section = _assign_section(page)
        sections[section].append(page)

    return dict(sections)


def _assign_section(page: PageInfo) -> str:
    if page.section and page.section != "Other":
        return _normalise(page.section)

    path = urlparse(page.url).path.strip("/")
    if not path:
        return "Home"

    parts = [p for p in path.split("/") if p]
    top = _normalise(parts[0])
    if top:
        return top

    if page.h1:
        return _normalise(page.h1)

    return "Other"


def _normalise(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()
