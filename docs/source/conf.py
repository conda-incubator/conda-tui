"""Documentation configuration for `conda-tui`."""

from __future__ import annotations

from conda_tui import __version__

# General information about the project.
project = "conda-tui"
author = "conda-tui team"
copyright = f"2023, {author}"
version = __version__
release = __version__

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
exclude_patterns: list[str] = []

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

autodoc_default_options = {
    "members": None,
    "undoc-members": None,
    "show-inheritance": None,
}

# The theme to use for HTML and HTML Help pages.
html_theme = "pydata_sphinx_theme"
# html_logo = "_static/images/logo.svg"
# html_favicon = "_static/images/favicon.ico"
html_theme_options = {
    "github_url": "https://github.com/anaconda-hackdays/conda-tui",
    "icon_links": [
        {
            "name": "channel",
            "url": "https://anaconda.org/mattkram/conda-tui",
            "icon": "fas fa-box",
        },
    ],
}
html_static_path = []
