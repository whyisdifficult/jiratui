# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from datetime import datetime

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'JiraTUI'
author = 'Gaston Tagni'
project_copyright = f'{datetime.now().year}, Gaston Tagni'
html_logo = '_static/assets/images/jiratui-logo.png'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_markdown_builder',
    'myst_parser',
    'sphinx_design',  # https://sphinx-design.readthedocs.io/en/rtd-theme/get_started.html
    'sphinxcontrib.mermaid',
]

templates_path = ['_templates']
exclude_patterns = ['_build']

language = 'en'

source_suffix = {
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Mermaid extension: https://github.com/mgaitan/sphinxcontrib-mermaid
# -- https://www.jsdelivr.com/package/npm/mermaid
mermaid_version = 'latest'
# -- https://www.jsdelivr.com/package/npm/@mermaid-js/layout-elk
mermaid_include_elk = '0.1.7'
