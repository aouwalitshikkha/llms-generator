from bs4 import BeautifulSoup

from llms_generator.page_analyzer import (
    extract_page_info,
    parse_meta_robots,
    parse_robots_header,
)
from llms_generator.section_grouper import group_pages


def test_parse_meta_robots_noindex():
    html = '<meta name="robots" content="noindex">'
    soup = BeautifulSoup(html, "html.parser")
    d = parse_meta_robots(soup)
    assert d.noindex is True
    assert d.nofollow is False


def test_parse_meta_robots_nofollow():
    html = '<meta name="robots" content="nofollow">'
    soup = BeautifulSoup(html, "html.parser")
    d = parse_meta_robots(soup)
    assert d.noindex is False
    assert d.nofollow is True


def test_parse_meta_robots_none():
    html = '<meta name="robots" content="noindex,nofollow">'
    soup = BeautifulSoup(html, "html.parser")
    d = parse_meta_robots(soup)
    assert d.noindex is True
    assert d.nofollow is True


def test_parse_robots_header_noindex():
    d = parse_robots_header("noindex")
    assert d.noindex is True
    assert d.nofollow is False


def test_parse_robots_header_nofollow():
    d = parse_robots_header("nofollow")
    assert d.noindex is False
    assert d.nofollow is True


def test_extract_page_info():
    html = """<html><head><title>Test Page</title>
    <meta name="description" content="A test page.">
    </head><body><h1>Test Heading</h1><p>Some content here.</p></body></html>"""
    info = extract_page_info("https://example.com/test", html, 1)
    assert info.title == "Test Page"
    assert info.h1 == "Test Heading"
    assert info.description == "A test page."
    assert "Test" in group_pages([info])


def test_extract_og_site_name():
    html = (
        '<html><head><meta property="og:site_name" content="Acme">'
        "</head><body><h1>H</h1><p>long enough content here for main text</p></body></html>"
    )
    info = extract_page_info("https://example.com/", html, 0)
    assert info.site_name == "Acme"
    assert info.full_text
