# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pathlib

# this path is pointing to astrogen/docs/source
CURRENT_PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
ASTROGEN_PATH = CURRENT_PATH.parent.parent

print(CURRENT_PATH)
print(ASTROGEN_PATH)

sys.path.insert(0, str(ASTROGEN_PATH))

from setup import VERSION
import astrogen

# -- Project information -----------------------------------------------------

project = 'astrogen'
copyright = '2021, Marcelo Lares'
author = 'Marcelo Lares'

version = VERSION
release = VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [ 'sphinx.ext.autodoc' ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_theme = 'insegel'
html_logo = "../source/img/astrogen_logo.svg"

html_static_path = []
