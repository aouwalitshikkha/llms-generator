from llms_generator.page_analyzer import PageInfo
from llms_generator.section_grouper import group_pages


def test_group_by_directory():
    pages = [
        PageInfo(url="https://example.com/docs/foo", section="Docs"),
        PageInfo(url="https://example.com/docs/bar", section="Docs"),
        PageInfo(url="https://example.com/blog/baz", section="Blog"),
    ]
    sections = group_pages(pages)
    assert "Docs" in sections
    assert "Blog" in sections
    assert len(sections["Docs"]) == 2
    assert len(sections["Blog"]) == 1


def test_group_empty():
    assert group_pages([]) == {}


def test_optional_classification():
    pages = [
        PageInfo(url="https://example.com/privacy-policy"),
        PageInfo(url="https://example.com/docs/x"),
    ]
    sections = group_pages(pages)
    assert "Optional" in sections
    assert "Docs" in sections
    assert len(sections["Optional"]) == 1


def test_optional_override():
    pages = [PageInfo(url="https://example.com/changelog/v1")]
    sections = group_pages(pages, optional_sections=["changelog"])
    assert "Optional" in sections
    assert len(sections["Optional"]) == 1
