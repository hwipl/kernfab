#!/usr/bin/env python3

"""
kernfab setup file
"""

import os
import re
import codecs

from setuptools import setup

# setup parameters
DESCRIPTION = "Linux kernel development tool based on fabric"
with open("README.md", 'r') as f:
    LONG_DESCRIPTION = f.read()
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]


# setup helpers
def read(*parts):
    """
    Read encoded file
    """

    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as enc_file:
        return enc_file.read()


def find_version(*file_paths):
    """
    Find version in encoded file
    """

    version_file = read(*file_paths)
    version_pattern = r"^VERSION = ['\"]([^'\"]*)['\"]"
    version_match = re.search(version_pattern, version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# run setup
setup(
    name="kernfab",
    version=find_version("kernfab", "main.py"),
    description=DESCRIPTION,
    license="MIT",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="hwipl",
    author_email="kernfab@hwipl.net",
    url="https://github.com/hwipl/kernfab",
    packages=["kernfab"],
    entry_points={
        "console_scripts": ["kernfab = kernfab.main:main"]
    },
    classifiers=CLASSIFIERS,
    python_requires=">=3.6",
    install_requires=["fabric"],
)
