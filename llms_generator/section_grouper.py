from __future__ import annotations

import re
from collections import defaultdict
from urllib.parse import urlparse

from llms_generator.page_analyzer import PageInfo

OPTIONAL_SECTION = "Optional"

_DEFAULT_OPTIONAL = frozenset(
    {
        "privacy",
        "privacypolicy",
        "terms",
        "termsofservice",
        "termsofuse",
        "tos",
        "legal",
        "cookies",
        "cookiepolicy",
        "imprint",
        "disclaimer",
        "eula",
        "gdpr",
        "dmca",
        "accessibility",
        "refund",
        "refunds",
        "returns",
        "tag",
        "tags",
        "author",
        "authors",
        "category",
        "categories",
        "archive",
        "archives",
        "feed",
        "rss",
        "sitemap",
        "search",
        "login",
        "signin",
        "signup",
        "register",
        "account",
        "cart",
        "checkout",
        "wishlist",
    }
)


def group_pages(
    pages: list[PageInfo],
    optional_sections: list[str] | None = None,
) -> dict[str, list[PageInfo]]:
    optional = {_key(name) for name in (optional_sections or [])}
    sections: dict[str, list[PageInfo]] = defaultdict(list)

    for page in pages:
        name = infer_section(page)
        if _is_optional(name, optional):
            name = OPTIONAL_SECTION
        sections[name].append(page)

    return dict(sections)


def infer_section(page: PageInfo) -> str:
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


def _is_optional(name: str, extra: set[str]) -> bool:
    key = _key(name)
    return key in _DEFAULT_OPTIONAL or key in extra


def _key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _normalise(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()
