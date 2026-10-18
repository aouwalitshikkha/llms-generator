from pathlib import Path

import pytest

from llms_generator import __version__
from llms_generator.cli import full_output_path, parse_args


def test_full_output_path_default():
    assert full_output_path("llms.txt") == Path("llms-full.txt")


def test_full_output_path_nested():
    assert full_output_path("public/llms.txt") == Path("public/llms-full.txt")


def test_parse_args_defaults():
    args = parse_args(["https://example.com"])
    assert args.url == "https://example.com"
    assert args.depth == 2
    assert args.timeout == 30.0
    assert args.max_pages == 0
    assert args.prefer_markdown is False
    assert args.check is False
    assert args.optional_paths == ""


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_args(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out
