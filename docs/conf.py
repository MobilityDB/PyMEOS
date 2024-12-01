# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PyMEOS"
copyright = "2023, Víctor Diví"
author = "Víctor Diví"
release = "1.2.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
import os
import sys

sys.path.insert(0, os.path.abspath("../pymeos_cffi"))
sys.path.insert(0, os.path.abspath("../pymeos"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_nb",
]

nb_execution_mode = "off"

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "_build",
    "**.ipynb_checkpoints",
]
autodoc_member_order = "bysource"

# -- Intersphinx config --------
intersphinx_mapping = {
    "asyncpg": ("https://magicstack.github.io/asyncpg/current/", None),
    "psycopg": ("https://www.psycopg.org/psycopg3/docs/", None),
    "psycopg2": ("https://www.psycopg.org/docs/", None),
    "shapely": ("https://shapely.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

import requests


def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Ensure we got a successful response

    # Ensure folder for destination file exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


prefix = "https://raw.githubusercontent.com/MobilityDB/PyMEOS-Examples/main/"
download_file(f"{prefix}PyMEOS_Examples/AIS.ipynb", "src/examples/AIS.ipynb")
download_file(
    f"{prefix}PyMEOS_Examples/BerlinMOD.ipynb", "src/examples/BerlinMOD.ipynb"
)
