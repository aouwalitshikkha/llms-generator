from llms_generator.validate import validate_llms_txt

VALID = """# Site

> Summary here.

## Docs

- [A](https://example.com/a): note
- [B](https://example.com/b)

## Optional

- [Terms](https://example.com/terms)
"""


def test_valid_file_has_no_problems():
    assert validate_llms_txt(VALID) == []


def test_missing_h1():
    problems = validate_llms_txt("> only a summary\n")
    assert any("H1" in p for p in problems)


def test_missing_blockquote():
    problems = validate_llms_txt("# Site\n\n## Docs\n\n- [A](https://x/a)\n")
    assert any("blockquote" in p for p in problems)


def test_malformed_entry():
    problems = validate_llms_txt("# Site\n\n> s\n\n## Docs\n\n- no link here\n")
    assert any("malformed" in p for p in problems)


def test_no_entries_under_section():
    problems = validate_llms_txt("# Site\n\n> s\n\n## Docs\n\n")
    assert any("No file-list entries" in p for p in problems)
