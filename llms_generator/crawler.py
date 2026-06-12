from __future__ import annotations

import random
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
        self._last_response_time: float = 0.0

    def run(self) -> list[PageInfo]:
        self._load_robots_txt()
        queue: deque[tuple[str, int]] = deque()
        start = self._normalize_url(self.start_url)
        queue.append((start, 0))
        self._visited.add(self._url_key(start))

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
                    self._visited.add(self._url_key(page.url))
                    links = self._extract_links(page.url, soup)
                    for link in links:
                        key = self._url_key(link)
                        if key not in self._visited:
                            self._visited.add(key)
                            queue.append((link, depth + 1))

                self._adaptive_sleep()
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
        html, final_url, header_nofollow = self._fetch(url)
        if html is None:
            return None

        soup = BeautifulSoup(html, "html.parser")

        directives = parse_meta_robots(soup)
        if directives.noindex:
            return None

        page = extract_page_info(final_url, html, depth, soup=soup)
        follow = not (directives.nofollow or header_nofollow)
        return page, soup, follow

    def _fetch(self, url: str) -> tuple[str | None, str, bool]:
        try:
            start = time.monotonic()
            resp = self._session.get(url, timeout=30)
            self._last_response_time = time.monotonic() - start
            final_url = resp.url
        except requests.RequestException:
            html, _ = self._fetch_with_playwright(url)
            return (html, url, False)

        if resp.status_code >= 400:
            return (None, url, False)

        ct = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" not in ct:
            return (None, url, False)

        header_nofollow = False
        x_robots = resp.headers.get("X-Robots-Tag")
        if x_robots:
            directives = parse_robots_header(x_robots)
            if directives.noindex:
                return (None, url, False)
            header_nofollow = directives.nofollow

        text = resp.text
        if not text or not text.strip():
            html, _ = self._fetch_with_playwright(url)
            return (html, final_url, header_nofollow)

        return (text, final_url, header_nofollow)

    def _adaptive_sleep(self) -> None:
        base = max(self.delay, 0.1)
        if self._last_response_time > 0:
            excess = self._last_response_time - base
            if excess > 0:
                base += min(excess, base * 2)
        jitter = random.uniform(-0.25, 0.25) * base
        time.sleep(max(0.1, base + jitter))

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
    #  URL normalization
    # ------------------------------------------------------------------
    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        base_parsed = urlparse(self._base)
        if parsed.scheme in ("http", "https") and base_parsed.scheme in ("http", "https"):
            parsed = parsed._replace(scheme=base_parsed.scheme)
        return parsed.geturl()

    def _url_key(self, url: str) -> str:
        url = self._normalize_url(url)
        parsed = urlparse(url)
        if parsed.path in ("", "/"):
            parsed = parsed._replace(path="")
        elif parsed.path.endswith("/"):
            parsed = parsed._replace(path=parsed.path.rstrip("/"))
        return parsed.geturl()

    # ------------------------------------------------------------------
    #  Link extraction
    # ------------------------------------------------------------------
    def _extract_links(self, base_url: str, soup: BeautifulSoup) -> list[str]:
        links: list[str] = []
        base_parsed = urlparse(self._base)

        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if not href:
                continue
            href = str(href)

            full = urljoin(base_url, href)
            parsed = urlparse(full)

            if parsed.netloc != base_parsed.netloc:
                continue
            if parsed.scheme not in ("http", "https"):
                continue
            if parsed.fragment:
                full = full[:full.index("#")]

            links.append(self._normalize_url(full))

        return list(dict.fromkeys(links))
