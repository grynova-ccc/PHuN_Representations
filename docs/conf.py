import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "PHuN Representations"
author = "Clara Kirkvold"
copyright = "2026, Clara Kirkvold"
release = "2026"

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"