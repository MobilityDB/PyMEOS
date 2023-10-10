# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PyMEOS'
copyright = '2023, Víctor Diví'
author = 'Víctor Diví'
release = '1.1.3b1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
import os
import sys

sys.path.insert(0, os.path.abspath('../pymeos_cffi'))
sys.path.insert(0, os.path.abspath('../pymeos'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autodoc_member_order = 'bysource'

# -- Intersphinx config --------
intersphinx_mapping = {
    'asyncpg': ('https://magicstack.github.io/asyncpg/current/', None),
    'psycopg': ('https://www.psycopg.org/psycopg3/docs/', None),
    'psycopg2': ('https://www.psycopg.org/docs/', None),
    'shapely': ('https://shapely.readthedocs.io/en/stable/', None),
    'python': ('https://docs.python.org/3', None)
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
