import os
import sys
sys.path.insert(0, os.path.abspath(".."))

project = "llms-generator"
copyright = "2026, aouwalitshikkha"
author = "aouwalitshikkha"
release = "0.2.0"

extensions = [
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}