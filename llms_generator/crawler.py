from __future__ import annotations

import time
import urllib.robotparser
from collections import deque
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from llms_generator._version import __version__
from llms_generator.page_analyzer import (
    PageInfo,
    extract_page_info,
    parse_meta_robots,
    parse_robots_header,
)

USER_AGENT = f"llms-generator/{__version__}"


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

        self._playwright = None
        self._playwright_browser = None

    def run(self) -> list[PageInfo]:
        self._load_robots_txt()
        queue: deque[tuple[str, int]] = deque()
        queue.append((self.start_url, 0))
        self._visited.add(self.start_url)

        try:
            while queue:
                url, depth = queue.popleft()
                if depth > self.max_depth:
                    continue

                if not self._is_allowed(url):
                    continue

                result = self._fetch_and_analyze(url, depth)
                if result is None:
                    continue

                page, soup, follow = result
                self._pages.append(page)

                if follow and depth < self.max_depth:
                    links = self._extract_links(url, soup)
                    for link in links:
                        if link not in self._visited:
                            self._visited.add(link)
                            queue.append((link, depth + 1))

                time.sleep(self.delay)
        finally:
            self._close_playwright()
            self._session.close()

        return self._pages

    # ------------------------------------------------------------------
    #  Robots.txt
    # ------------------------------------------------------------------
    def _load_robots_txt(self) -> None:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(self._base, "/robots.txt"))
        try:
            rp.read()
            if not rp.entries:
                rp = None
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
    def _fetch_and_analyze(self, url: str, depth: int) -> tuple[PageInfo, BeautifulSoup, bool] | None:
        html, header_nofollow = self._fetch(url)
        if html is None:
            return None

        soup = BeautifulSoup(html, "html.parser")

        directives = parse_meta_robots(soup)
        if directives.noindex:
            return None

        page = extract_page_info(url, html, depth, soup=soup)
        follow = not (directives.nofollow or header_nofollow)
        return page, soup, follow

    def _fetch(self, url: str) -> tuple[str | None, bool]:
        try:
            resp = self._session.get(url, timeout=30)
        except requests.RequestException:
            return self._fetch_with_playwright(url)

        if resp.status_code >= 400:
            return (None, False)

        ct = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" not in ct:
            return (None, False)

        header_nofollow = False
        x_robots = resp.headers.get("X-Robots-Tag")
        if x_robots:
            directives = parse_robots_header(x_robots)
            if directives.noindex:
                return (None, False)
            header_nofollow = directives.nofollow

        text = resp.text
        if not text or not text.strip():
            html, _ = self._fetch_with_playwright(url)
            return (html, header_nofollow)

        return (text, header_nofollow)

    def _fetch_with_playwright(self, url: str) -> tuple[str | None, bool]:
        if not self.use_js:
            return (None, False)

        browser = self._ensure_playwright_browser()
        if browser is None:
            return (None, False)

        try:
            pw_page = browser.new_page(user_agent=USER_AGENT)
            try:
                pw_page.goto(url, timeout=30000, wait_until="domcontentloaded")
                return (pw_page.content(), False)
            except Exception:
                return (None, False)
            finally:
                pw_page.close()
        except Exception:
            return (None, False)

    def _ensure_playwright_browser(self):
        if self._playwright_browser is not None:
            return self._playwright_browser
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return None
        try:
            self._playwright = sync_playwright()
            pw = self._playwright.start()
            self._playwright_browser = pw.chromium.launch(headless=True)
            return self._playwright_browser
        except Exception:
            self._close_playwright()
            return None

    def _close_playwright(self):
        try:
            if self._playwright_browser is not None:
                self._playwright_browser.close()
        except Exception:
            pass
        try:
            if self._playwright is not None:
                self._playwright.__exit__(None, None, None)
        except Exception:
            pass
        self._playwright_browser = None
        self._playwright = None

    # ------------------------------------------------------------------
    #  Link extraction
    # ------------------------------------------------------------------
    def _extract_links(self, base_url: str, soup: BeautifulSoup) -> list[str]:
        links: list[str] = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if not href:
                continue
            href = str(href)

            full = urljoin(base_url, href)
            parsed = urlparse(full)

            if parsed.netloc != urlparse(self._base).netloc:
                continue
            if parsed.scheme not in ("http", "https"):
                continue
            if parsed.fragment:
                full = full[:full.index("#")]

            links.append(full)

        return list(dict.fromkeys(links))
