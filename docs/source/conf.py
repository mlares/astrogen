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
ASTROGEN_DATA_PATH = CURRENT_PATH.parent.parent / 'astrogen/data/'
ASTROGEN_VIZ_PATH = CURRENT_PATH.parent.parent / 'astrogen/dataviz/'

print(CURRENT_PATH)
print(ASTROGEN_DATA_PATH)

sys.path.insert(0, str(ASTROGEN_DATA_PATH))
sys.path.insert(0, str(ASTROGEN_VIZ_PATH))
sys.path.insert(0, '.')
sys.path.insert(0, '..')

autodoc_mock_imports = ['numpy',
                        'time',
                        'datetime',
                        'pandas',
                        'jellyfish',
                        'bonobo',
                        'dateutil',
                        'openpyxl',
                        'scipy',
                        'ads',
                        'Parser',
                        'astrogen_tools'
                       ]


# import datetime
# import time
# import pandas as pd
# import bonobo
# import numpy as np
# from dateutil.relativedelta import relativedelta
# import numpy as np
# from scipy.optimize import curve_fit
# from astrogen.data.astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
# from astrogen.data.astrogen_utils import initials, getinitials, pickone
# import pickle
# import ads
# from sys import argv
# #from Parser import Parser
# from astrogen.data.Parser import Parser
# 
# # avoid SettingWithCopyWarning
# # (see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy)
# pd.options.mode.chained_assignment = None


# -- Project information -----------------------------------------------------

project = 'astrogen'
copyright = '2021, Marcelo Lares'
author = 'Marcelo Lares'

version = '0.1'
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
#html_logo = "../source/img/astrogen_logo.svg"

html_static_path = []

master_doc = 'index'
