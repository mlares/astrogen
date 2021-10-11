# ===========================================================
# DOCS
# ===========================================================

"""Utilities to analyse gender data in astronomy in Argentina

"""


# ===========================================================
# IMPORTS
# ===========================================================

import pathlib
import os

# from ez_setup import use_setuptools
# use_setuptools()

from setuptools import setup, find_packages

# ===========================================================
# CONSTANTS
# ===========================================================

PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))

REQUIREMENTS = [
    "numpy",
    "attrs",
    "pandas",
    "joblib",
    "matplotlib"]


with open(PATH / "README.rst") as fp:
    LONG_DESCRIPTION = fp.read()
 
DESCRIPTION = (
    "Analyze gender data for the astronomical community in Argentina"
    )

with open(PATH / "astrogen" / "__init__.py") as fp:
    for line in fp.readlines():
        if line.startswith("__version__ = "):
            VERSION = line.split("=", 1)[-1].replace('"', '').strip()
            break
 
# ===========================================================
# FUNCTIONS
# ===========================================================

# setup(name="astrogen", packages=find_packages())

def do_setup():
    setup(
        name="astrogen",
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',

        author=[
            "Marcelo Lares"],
        author_email="marcelo.lares@unc.edu.ar",
        url="https://github.com/mlares/astrogen",
        license="MIT",

        keywords=["data analysis"],

        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Scientific/Engineering"],

        packages=["astrogen"],
        py_modules=["ez_setup"],

        install_requires=REQUIREMENTS)


if __name__ == "__main__":
    do_setup()
