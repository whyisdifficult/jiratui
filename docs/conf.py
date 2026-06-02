# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from datetime import datetime
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'JiraTUI'
author = 'Gaston Tagni'
project_copyright = f'{datetime.now().year}, Gaston Tagni'
html_logo = '_static/assets/images/jiratui-logo.png'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath('../'))

extensions = [
    'sphinx_markdown_builder',
    'myst_parser',
    'sphinx_design',  # https://sphinx-design.readthedocs.io/en/rtd-theme/get_started.html
    'sphinxcontrib.mermaid',
    'autodoc2',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_togglebutton',  # https://github.com/executablebooks/sphinx-togglebutton
]

templates_path = ['_templates']
exclude_patterns = ['_build']

language = 'en'

source_suffix = {
    '.md': 'markdown',
}

# -- Intersphinx Configuration -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Mermaid extension: https://github.com/mgaitan/sphinxcontrib-mermaid
# -- https://www.jsdelivr.com/package/npm/mermaid
mermaid_version = 'latest'
# -- https://www.jsdelivr.com/package/npm/@mermaid-js/layout-elk
mermaid_include_elk = True

napoleon_google_docstring = True
napoleon_numpy_docstring = False

# autodoc2 configuration
autodoc2_docstring_parser_regexes = [
    (
        r'.*',
        'docs.extensions.docstrings_parser',
    )
]
autodoc2_packages = [
    {'path': 'jiratui', 'auto_mode': False},
    # {
    #     'path': 'developers',
    #     'auto_mode': False
    # }
]
autodoc2_render_plugin = 'myst'
autodoc2_hidden_objects = ['undoc', 'dunder', 'private', 'inherited']
autodoc2_docstring = 'all'

myst_heading_anchors = 6
myst_highlight_code_blocks = True
myst_number_code_blocks = ['python']
myst_enable_extensions = ['fieldlist']
