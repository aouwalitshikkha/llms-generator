from llms_generator.generator import generate_llms_txt
from llms_generator.page_analyzer import PageInfo


def test_generates_valid_llms_txt():
    pages = [
        PageInfo(
            url="https://example.com/",
            title="Example Site",
            h1="Welcome",
            summary="A great example site.",
            section="Home",
        ),
        PageInfo(
            url="https://example.com/docs",
            title="Docs – Example Site",
            h1="Documentation",
            summary="How-to guides.",
            section="Docs",
        ),
    ]
    sections = {"Home": [pages[0]], "Docs": [pages[1]]}
    output = generate_llms_txt(sections)

    assert "# Example Site" in output
    assert "## Home" in output
    assert "## Docs" in output
    assert "https://example.com/" in output
    assert "https://example.com/docs" in output
