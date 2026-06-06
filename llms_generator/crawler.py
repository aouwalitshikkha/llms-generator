from __future__ import annotations

import time
import urllib.robotparser
from collections import deque
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from llms_generator.page_analyzer import (
    PageInfo,
    RobotsDirectives,
    extract_page_info,
    parse_meta_robots,
    parse_robots_header,
)

USER_AGENT = "llms-generator/0.1.0"


class Crawler:
    def __init__(
        self,
        start_url: str,
        max_depth: int = 2,
        delay: float = 1.0,
        use_js: bool = True,
    ):
        self.start_url = start_url.rstrip("/")
        self.max_depth = max_depth
        self.delay = delay
        self.use_js = use_js
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

        parsed = urlparse(self.start_url)
        self._base = f"{parsed.scheme}://{parsed.netloc}"

        self._rp: Optional[urllib.robotparser.RobotFileParser] = None
        self._visited: set[str] = set()
        self._pages: list[PageInfo] = []

    def run(self) -> list[PageInfo]:
        self._load_robots_txt()
        queue: deque[tuple[str, int]] = deque()
        queue.append((self.start_url, 0))
        self._visited.add(self.start_url)

        while queue:
            url, depth = queue.popleft()
            if depth > self.max_depth:
                continue

            if not self._is_allowed(url):
                continue

            page = self._fetch_and_analyze(url, depth)
            if page is None:
                continue

            self._pages.append(page)

            if depth < self.max_depth:
                links = self._extract_links(url, page.raw_html)
                for link in links:
                    if link not in self._visited:
                        self._visited.add(link)
                        queue.append((link, depth + 1))

            time.sleep(self.delay)

        return self._pages

    # ------------------------------------------------------------------
    #  Robots.txt
    # ------------------------------------------------------------------
    def _load_robots_txt(self) -> None:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(self._base, "/robots.txt"))
        try:
            rp.read()
        except Exception:
            rp = None
        self._rp = rp

    def _is_allowed(self, url: str) -> bool:
        if self._rp is None:
            return True
        try:
            return self._rp.can_fetch(USER_AGENT, url)
        except Exception:
            return True

    # ------------------------------------------------------------------
    #  Fetch + analyze
    # ------------------------------------------------------------------
    def _fetch_and_analyze(self, url: str, depth: int) -> PageInfo | None:
        html = self._fetch(url)
        if html is None:
            return None

        page = extract_page_info(url, html, depth)

        directives = self._check_robots_directives(html)
        if directives.noindex:
            return None

        return page

    def _fetch(self, url: str) -> str | None:
        try:
            resp = self._session.get(url, timeout=30)
            resp.raise_for_status()
        except requests.RequestException:
            return self._fetch_with_playwright(url)

        ct = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" not in ct:
            return None

        # Check X-Robots-Tag header
        x_robots = resp.headers.get("X-Robots-Tag")
        if x_robots:
            directives = parse_robots_header(x_robots)
            if directives.noindex:
                return None

        return resp.text

    def _fetch_with_playwright(self, url: str) -> str | None:
        if not self.use_js:
            return None
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=USER_AGENT)
                try:
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    content = page.content()
                except Exception:
                    return None
                finally:
                    browser.close()
                return content
        except Exception:
            return None

    # ------------------------------------------------------------------
    #  Link extraction
    # ------------------------------------------------------------------
    def _extract_links(self, base_url: str, html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []

        directives = self._check_robots_directives(html)
        if directives.nofollow:
            return links

        for a_tag in soup.find_all("a", href=True):
            if not isinstance(a_tag, Tag):
                continue
            href = a_tag["href"]
            if isinstance(href, (list, tuple)):
                href = href[0] if href else ""
            href = str(href)

            # Resolve relative URLs
            full = urljoin(base_url, href)
            parsed = urlparse(full)

            # Same domain only, skip fragments, skip non-HTTP(S)
            if parsed.netloc != urlparse(self._base).netloc:
                continue
            if parsed.scheme not in ("http", "https"):
                continue
            if parsed.fragment:
                full = full.rstrip("#" + parsed.fragment)

            links.append(full)

        return list(dict.fromkeys(links))  # deduplicate, preserve order

    # ------------------------------------------------------------------
    #  Robots directives from HTML
    # ------------------------------------------------------------------
    @staticmethod
    def _check_robots_directives(html: str) -> RobotsDirectives:
        soup = BeautifulSoup(html, "html.parser")
        return parse_meta_robots(soup)
