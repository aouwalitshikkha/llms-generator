from __future__ import annotations

import logging
import random
import time
import urllib.robotparser
from collections import deque
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse

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
ROBOTS_UA = "llms-generator"

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_RETRIES = 3
MAX_RETRY_DELAY = 30.0

TRACKING_PARAMS = frozenset(
    {
        "fbclid",
        "gclid",
        "dclid",
        "gbraid",
        "wbraid",
        "msclkid",
        "yclid",
        "twclid",
        "igshid",
        "mc_cid",
        "mc_eid",
        "mkt_tok",
        "_ga",
        "_gl",
        "_hsenc",
        "_hsmi",
        "vero_conv",
        "vero_id",
        "oly_anon_id",
        "oly_enc_id",
        "icid",
        "scid",
        "cmpid",
        "campaignid",
        "spm",
        "ref",
        "ref_src",
        "ref_url",
        "srsltid",
        "s_kwcid",
        "ef_id",
        "trk",
        "trkcampaign",
    }
)
TRACKING_PREFIXES = ("utm_", "pk_", "mtm_", "hsa_", "piwik_", "matomo_", "ga_")

log = logging.getLogger("llms_generator")


def _is_tracking_param(name: str) -> bool:
    name = name.lower()
    return name in TRACKING_PARAMS or name.startswith(TRACKING_PREFIXES)


def _canonical_netloc(parsed) -> str:
    host = parsed.hostname or ""
    if not host:
        return parsed.netloc
    port = parsed.port
    if port is None:
        return host
    if (parsed.scheme == "http" and port == 80) or (parsed.scheme == "https" and port == 443):
        return host
    return f"{host}:{port}"


def _rel_tokens(tag) -> list[str]:
    rel = tag.get("rel")
    if isinstance(rel, str):
        return rel.split()
    if rel:
        return [str(token) for token in rel]
    return []


def _markdown_alternate(base_url: str, soup: BeautifulSoup) -> str | None:
    for link in soup.find_all("link", href=True):
        if "alternate" not in _rel_tokens(link):
            continue
        types = str(link.get("type") or "").lower()
        if "markdown" in types:
            return urljoin(base_url, str(link.get("href")))
    return None


class Crawler:
    def __init__(
        self,
        start_url: str,
        max_depth: int = 2,
        delay: float = 1.0,
        use_js: bool = True,
        timeout: float = 30.0,
        max_pages: int = 0,
        prefer_markdown: bool = False,
    ):
        self.start_url = start_url.rstrip("/")
        self.max_depth = max_depth
        self.delay = delay
        self.use_js = use_js
        self.timeout = timeout
        self.max_pages = max_pages
        self.prefer_markdown = prefer_markdown
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

        parsed = urlparse(self.start_url)
        self._base = f"{parsed.scheme}://{_canonical_netloc(parsed)}"
        self._base_netloc = urlparse(self._base).netloc

        self._rp: urllib.robotparser.RobotFileParser | None = None
        self._crawl_delay: float | None = None
        self._visited: set[str] = set()
        self._pages: list[PageInfo] = []

        self._playwright = None
        self._playwright_browser = None
        self._last_response_time: float = 0.0

    def run(self) -> list[PageInfo]:
        self._pages = []
        self._visited = set()
        self._load_robots_txt()

        queue: deque[tuple[str, int]] = deque()
        start = self._normalize_url(self.start_url)
        queue.append((start, 0))
        self._visited.add(self._url_key(start))

        try:
            while queue:
                if self.max_pages and len(self._pages) >= self.max_pages:
                    log.warning("Reached --max-pages limit (%d); stopping crawl.", self.max_pages)
                    break

                url, depth = queue.popleft()
                if depth > self.max_depth:
                    continue

                if not self._is_allowed(url):
                    log.debug("Blocked by robots.txt: %s", url)
                    continue

                result = self._fetch_and_analyze(url, depth)
                if result is None:
                    continue

                page, soup, follow = result
                self._pages.append(page)
                log.debug("Crawled [d=%d] %s", depth, page.url)

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
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(urljoin(self._base, "/robots.txt"))
        result: urllib.robotparser.RobotFileParser | None = parser
        try:
            parser.read()
            if not getattr(parser, "entries", None):
                result = None
        except Exception as exc:
            log.debug("Could not read robots.txt (%s); allowing all paths.", exc)
            result = None
        self._rp = result
        if result is not None:
            try:
                delay = result.crawl_delay(ROBOTS_UA)
                self._crawl_delay = float(delay) if delay is not None else None
            except (TypeError, ValueError):
                self._crawl_delay = None

    def _is_allowed(self, url: str) -> bool:
        if self._rp is None:
            return True
        try:
            return self._rp.can_fetch(ROBOTS_UA, url)
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
            log.debug("Skipping noindex page: %s", final_url)
            return None

        page = extract_page_info(self._normalize_url(final_url), html, depth, soup=soup)
        if self.prefer_markdown:
            alternate = _markdown_alternate(page.url, soup)
            if alternate:
                page.url = self._normalize_url(alternate)
        follow = not (directives.nofollow or header_nofollow)
        return page, soup, follow

    def _fetch(self, url: str) -> tuple[str | None, str, bool]:
        resp = self._get_with_retries(url)
        if resp is None:
            html, _ = self._fetch_with_playwright(url)
            return (html, url, False)

        final_url = resp.url
        if urlparse(final_url).netloc != self._base_netloc:
            log.debug("Skipping off-domain redirect: %s -> %s", url, final_url)
            return (None, url, False)

        if resp.status_code >= 400:
            return (None, url, False)

        ct = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" not in ct and not self._looks_like_html(resp):
            return (None, url, False)

        header_nofollow = False
        x_robots = resp.headers.get("X-Robots-Tag")
        if x_robots:
            directives = parse_robots_header(x_robots)
            if directives.noindex:
                return (None, url, False)
            header_nofollow = directives.nofollow

        if resp.encoding is None or "charset" not in ct:
            apparent = resp.apparent_encoding
            if apparent:
                resp.encoding = apparent

        text = resp.text
        if not text or not text.strip():
            html, _ = self._fetch_with_playwright(url)
            return (html, final_url, header_nofollow)

        return (text, final_url, header_nofollow)

    def _get_with_retries(self, url: str) -> requests.Response | None:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                start = time.monotonic()
                resp = self._session.get(url, timeout=self.timeout)
                self._last_response_time = time.monotonic() - start
            except requests.RequestException as exc:
                log.debug("Request error for %s (attempt %d/%d): %s", url, attempt, MAX_RETRIES, exc)
                if attempt < MAX_RETRIES:
                    self._retry_sleep(attempt, None)
                continue

            if resp.status_code in RETRY_STATUSES and attempt < MAX_RETRIES:
                log.debug(
                    "Retryable status %d for %s (attempt %d/%d)",
                    resp.status_code,
                    url,
                    attempt,
                    MAX_RETRIES,
                )
                self._retry_sleep(attempt, resp.headers.get("Retry-After"))
                continue

            return resp

        return None

    def _retry_sleep(self, attempt: int, retry_after: str | None) -> None:
        delay = max(self.delay, 0.1) * (2 ** (attempt - 1))
        if retry_after:
            try:
                delay = max(delay, float(retry_after))
            except ValueError:
                pass
        time.sleep(min(max(0.1, delay), MAX_RETRY_DELAY))

    @staticmethod
    def _looks_like_html(resp: requests.Response) -> bool:
        try:
            head = resp.content[:512].lstrip().lower()
        except Exception:
            return False
        return head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<html" in head

    def _adaptive_sleep(self) -> None:
        base = max(self.delay, self._crawl_delay or 0.0, 0.1)
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
                pw_page.goto(url, timeout=int(self.timeout * 1000), wait_until="domcontentloaded")
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
            self._playwright = sync_playwright().start()
            self._playwright_browser = self._playwright.chromium.launch(headless=True)
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
                self._playwright.stop()
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
        if parsed.netloc:
            parsed = parsed._replace(netloc=_canonical_netloc(parsed))
        if parsed.query:
            pairs = parse_qsl(parsed.query, keep_blank_values=True)
            kept = sorted((k, v) for k, v in pairs if not _is_tracking_param(k))
            parsed = parsed._replace(query=urlencode(kept))
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

        for a_tag in soup.find_all("a", href=True):
            if any(token in ("nofollow", "ugc", "sponsored") for token in _rel_tokens(a_tag)):
                continue

            href = a_tag.get("href")
            if not href:
                continue
            href = str(href)

            full = urljoin(base_url, href)
            if "#" in full:
                full = full.split("#", 1)[0]

            normalized = self._normalize_url(full)
            parsed = urlparse(normalized)

            if parsed.netloc != self._base_netloc:
                continue
            if parsed.scheme not in ("http", "https"):
                continue

            links.append(normalized)

        return list(dict.fromkeys(links))
