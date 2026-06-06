from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag


@dataclass
class PageInfo:
    url: str
    title: str = ""
    h1: str = ""
    description: str = ""
    summary: str = ""
    section: str = ""
    depth: int = 0
    full_text: str = ""
    raw_html: str = ""


@dataclass
class RobotsDirectives:
    noindex: bool = False
    nofollow: bool = False


_X_ROBOTS_TAG_RE = re.compile(
    r"(?:noindex|nofollow|index|follow|none|all|noarchive)",
    re.IGNORECASE,
)


def parse_robots_header(header_value: str) -> RobotsDirectives:
    d = RobotsDirectives()
    val = header_value.lower()
    if "none" in val:
        d.noindex = True
        d.nofollow = True
    if "noindex" in val:
        d.noindex = True
    if "nofollow" in val:
        d.nofollow = True
    return d


def parse_meta_robots(soup: BeautifulSoup) -> RobotsDirectives:
    d = RobotsDirectives()
    meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    if not meta or not isinstance(meta, Tag):
        return d
    content = (meta.get("content") or "").lower()
    if "none" in content:
        d.noindex = True
        d.nofollow = True
    if "noindex" in content:
        d.noindex = True
    if "nofollow" in content:
        d.nofollow = True
    return d


def extract_page_info(url: str, html: str, depth: int) -> PageInfo:
    soup = BeautifulSoup(html, "html.parser")
    info = PageInfo(url=url, depth=depth, raw_html=html)

    title_tag = soup.find("title")
    if title_tag and isinstance(title_tag, Tag):
        info.title = title_tag.get_text(strip=True)

    h1_tag = soup.find("h1")
    if h1_tag:
        info.h1 = h1_tag.get_text(strip=True)

    meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if meta_desc and isinstance(meta_desc, Tag):
        info.description = (meta_desc.get("content") or "").strip()

    info.summary = info.description or info.h1 or info.title

    p_tag = soup.find("p")
    if p_tag:
        text = p_tag.get_text(strip=True)
        if len(text) > 20:
            info.full_text = text
        else:
            info.full_text = _find_first_meaningful_text(soup)

    info.section = _infer_section(url, info.h1)
    return info


def _find_first_meaningful_text(soup: BeautifulSoup) -> str:
    for tag in soup.find_all(["p", "li", "div", "section"]):
        text = tag.get_text(strip=True)
        if len(text) > 50:
            return text[:500]
    return ""


def _infer_section(url: str, h1: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "Home"
    parts = path.split("/")
    top = parts[0].replace("-", " ").replace("_", " ").title()
    if top:
        return top
    return h1 or "Other"
