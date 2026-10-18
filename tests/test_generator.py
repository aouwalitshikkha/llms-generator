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


def test_optional_section_is_last():
    sections = {
        "Optional": [PageInfo(url="https://e.com/privacy", title="Privacy")],
        "Docs": [PageInfo(url="https://e.com/docs", title="Docs")],
    }
    output = generate_llms_txt(sections)
    assert output.index("## Docs") < output.index("## Optional")


def test_redundant_description_omitted():
    sections = {"Docs": [PageInfo(url="https://e.com/docs", title="Docs", summary="Docs")]}
    output = generate_llms_txt(sections)
    assert "- [Docs](https://e.com/docs)" in output
    assert "- [Docs](https://e.com/docs): Docs" not in output


def test_site_name_prefers_og_site_name():
    sections = {"Home": [PageInfo(url="https://e.com/", title="Some Title", site_name="Acme Corp")]}
    output = generate_llms_txt(sections)
    assert output.startswith("# Acme Corp")
