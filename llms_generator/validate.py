from __future__ import annotations

import re

_H1_RE = re.compile(r"^#\s+\S")
_H2_RE = re.compile(r"^##\s+\S")
_LINK_RE = re.compile(r"^- \[[^\]]+\]\([^)\s]+\)(?::\s*.*)?$")


def validate_llms_txt(text: str) -> list[str]:
    """Return a list of spec-compliance problems. Empty list means valid."""
    problems: list[str] = []
    content = text.lstrip("\ufeff")
    lines = content.splitlines()
    non_empty = [line for line in lines if line.strip()]

    if not non_empty or not _H1_RE.match(non_empty[0]):
        problems.append("First non-empty line must be an H1 heading (# Site name).")

    if not any(line.startswith("> ") for line in lines):
        problems.append("Missing blockquote summary line (starting with '> ').")

    seen_h2 = False
    entries = 0
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if _H2_RE.match(line):
            seen_h2 = True
            continue
        if seen_h2 and stripped.startswith("- "):
            entries += 1
            if not _LINK_RE.match(stripped):
                problems.append(f"Line {idx}: malformed file-list entry: {stripped}")

    if seen_h2 and entries == 0:
        problems.append("No file-list entries found under any section.")

    return problems
