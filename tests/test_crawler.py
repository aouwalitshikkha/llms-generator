import urllib.robotparser

import pytest
import responses

from llms_generator.crawler import Crawler

BASE = "https://site.test"
ROOT = BASE + "/"


@pytest.fixture
def no_wait(monkeypatch):
    monkeypatch.setattr(Crawler, "_load_robots_txt", lambda self: None)
    monkeypatch.setattr(Crawler, "_adaptive_sleep", lambda self: None)


def _crawler(**kwargs) -> Crawler:
    kwargs.setdefault("delay", 0)
    kwargs.setdefault("use_js", False)
    return Crawler(BASE, **kwargs)


@responses.activate(assert_all_requests_are_fired=False)
def test_max_depth_limits_crawl(no_wait):
    responses.add(responses.GET, BASE, body='<a href="/a">A</a><a href="/b">B</a>', content_type="text/html")
    responses.add(responses.GET, BASE + "/a", body='<a href="/c">C</a>', content_type="text/html")
    responses.add(responses.GET, BASE + "/b", body='<a href="/c">C</a>', content_type="text/html")
    responses.add(responses.GET, BASE + "/c", body="<p>c</p>", content_type="text/html")

    pages = _crawler(max_depth=1).run()
    assert {p.url for p in pages} == {ROOT, BASE + "/a", BASE + "/b"}


@responses.activate(assert_all_requests_are_fired=False)
def test_tracking_params_are_deduplicated(no_wait):
    responses.add(
        responses.GET,
        BASE,
        body='<a href="/a?utm_source=x">A</a><a href="/a">A2</a>',
        content_type="text/html",
    )
    responses.add(responses.GET, BASE + "/a", body="<p>a</p>", content_type="text/html")

    pages = _crawler(max_depth=1).run()
    assert len(pages) == 2


@responses.activate(assert_all_requests_are_fired=False)
def test_per_link_nofollow_not_followed(no_wait):
    responses.add(
        responses.GET,
        BASE,
        body='<a href="/a">A</a><a href="/b" rel="nofollow">B</a>',
        content_type="text/html",
    )
    responses.add(responses.GET, BASE + "/a", body="<p>a</p>", content_type="text/html")
    responses.add(responses.GET, BASE + "/b", body="<p>b</p>", content_type="text/html")

    pages = _crawler(max_depth=1).run()
    assert {p.url for p in pages} == {ROOT, BASE + "/a"}


@responses.activate(assert_all_requests_are_fired=False)
def test_meta_noindex_page_skipped(no_wait):
    responses.add(
        responses.GET,
        BASE,
        body='<a href="/a">A</a><a href="/b">B</a>',
        content_type="text/html",
    )
    responses.add(
        responses.GET,
        BASE + "/a",
        body='<meta name="robots" content="noindex"><p>a</p>',
        content_type="text/html",
    )
    responses.add(responses.GET, BASE + "/b", body="<p>b</p>", content_type="text/html")

    pages = _crawler(max_depth=1).run()
    assert {p.url for p in pages} == {ROOT, BASE + "/b"}


@responses.activate(assert_all_requests_are_fired=False)
def test_header_noindex_page_skipped(no_wait):
    responses.add(responses.GET, BASE, body='<a href="/a">A</a>', content_type="text/html")
    responses.add(
        responses.GET,
        BASE + "/a",
        body="<p>a</p>",
        content_type="text/html",
        headers={"X-Robots-Tag": "noindex"},
    )

    pages = _crawler(max_depth=1).run()
    assert {p.url for p in pages} == {ROOT}


@responses.activate(assert_all_requests_are_fired=False)
def test_off_domain_redirect_skipped(no_wait):
    responses.add(responses.GET, BASE, body='<a href="/x">X</a>', content_type="text/html")
    responses.add(
        responses.GET,
        BASE + "/x",
        status=302,
        headers={"Location": "https://other.test/"},
    )
    responses.add(responses.GET, "https://other.test/", body="<p>other</p>", content_type="text/html")

    pages = _crawler(max_depth=1).run()
    assert {p.url for p in pages} == {ROOT}


@responses.activate(assert_all_requests_are_fired=False)
def test_max_pages_limit(no_wait):
    responses.add(
        responses.GET,
        BASE,
        body='<a href="/a">A</a><a href="/b">B</a><a href="/c">C</a>',
        content_type="text/html",
    )
    for path in ("/a", "/b", "/c"):
        responses.add(responses.GET, BASE + path, body="<p>x</p>", content_type="text/html")

    pages = _crawler(max_depth=1, max_pages=2).run()
    assert len(pages) == 2


@responses.activate(assert_all_requests_are_fired=False)
def test_robots_disallow_blocks_path(no_wait):
    responses.add(responses.GET, BASE, body='<a href="/a">A</a><a href="/b">B</a>', content_type="text/html")
    responses.add(responses.GET, BASE + "/b", body="<p>b</p>", content_type="text/html")

    crawler = _crawler(max_depth=1)
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(["User-agent: *", "Disallow: /a"])
    crawler._rp = rp

    pages = crawler.run()
    assert {p.url for p in pages} == {ROOT, BASE + "/b"}


@responses.activate(assert_all_requests_are_fired=False)
def test_default_https_port_normalized(no_wait):
    responses.add(responses.GET, BASE, body='<a href="https://site.test:443/a">A</a>', content_type="text/html")
    responses.add(responses.GET, BASE + "/a", body="<p>a</p>", content_type="text/html")

    pages = _crawler(max_depth=1).run()
    assert {p.url for p in pages} == {ROOT, BASE + "/a"}
