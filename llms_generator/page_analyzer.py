from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

_MAX_FULL_TEXT = 2000

_BOILERPLATE_TAGS = ("nav", "header", "footer", "aside", "script", "style", "noscript", "form", "template")


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
    site_name: str = ""


@dataclass
class RobotsDirectives:
    noindex: bool = False
    nofollow: bool = False


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
    content = str(meta.get("content") or "").lower()
    if "none" in content:
        d.noindex = True
        d.nofollow = True
    if "noindex" in content:
        d.noindex = True
    if "nofollow" in content:
        d.nofollow = True
    return d


def extract_page_info(url: str, html: str, depth: int, soup: BeautifulSoup | None = None) -> PageInfo:
    if soup is None:
        soup = BeautifulSoup(html, "html.parser")
    info = PageInfo(url=url, depth=depth)

    title_tag = soup.find("title")
    if title_tag and isinstance(title_tag, Tag):
        info.title = title_tag.get_text(strip=True)

    h1_tag = soup.find("h1")
    if h1_tag and isinstance(h1_tag, Tag):
        info.h1 = h1_tag.get_text(strip=True)

    meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if meta_desc and isinstance(meta_desc, Tag):
        info.description = str(meta_desc.get("content") or "").strip()

    info.summary = info.description or info.h1 or info.title
    info.site_name = _extract_site_name(soup)
    info.full_text = _extract_main_text(soup)
    return info


def _extract_site_name(soup: BeautifulSoup) -> str:
    og = soup.find("meta", attrs={"property": re.compile(r"^og:site_name$", re.I)})
    if not og:
        og = soup.find("meta", attrs={"name": re.compile(r"^og:site_name$", re.I)})
    if og and isinstance(og, Tag):
        return str(og.get("content") or "").strip()
    return ""


def _extract_main_text(soup: BeautifulSoup, limit: int = _MAX_FULL_TEXT) -> str:
    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find(None, {"role": "main"})
        or soup.body
        or soup
    )
    try:
        clone = BeautifulSoup(str(container), "html.parser")
    except Exception:
        return ""
    for tag in clone.find_all(_BOILERPLATE_TAGS):
        tag.decompose()
    text = clone.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]
