#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path
import io

pwd = path.abspath(path.dirname(__file__))
with io.open(path.join(pwd, "README.md"), encoding="utf-8") as readme:
    desc = readme.read()

setup(
    name="crawlmap",
    version="1.2",
    description="A python3 script to change your crawling logs to a mindmap",
    long_description=desc,
    long_description_content_type="text/markdown",
    author="Liodeus",
    license="GPL-3.0 License",
    url="https://github.com/Liodeus/Crawlmap",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
    ],
    entry_points={
        "console_scripts": [
            "crawlmap = crawlmap.__main__:main"
        ]
    },
    install_requires=["haralyzer"],
    keywords=["python", "pentesting", "bugbounty", "security", "mindmap", "crawl", "crawling"],
)