# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'msi2slstr'
copyright = '2024, Joseph Doundoulakis'
author = 'Joseph Doundoulakis'
release = '0.0.0-beta'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'myst_parser' 
    ]

templates_path = ['_templates']
exclude_patterns = []

autodoc_member_order = "bysource"

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'logo': None,
    'github_user': 'josephdoun',
    'github_repo': 'msi2slstr',
    'description': 'AI-based datafusion of S2L1C/S3RBT-LST satellite data.'
}

import sys, os

sys.path.insert(0, os.path.abspath("../../src/msi2slstr"))

