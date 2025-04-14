# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : setup.py
@Project  : 
@Time     : 2025/4/10 16:22
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from pathlib import Path

from setuptools import find_packages, setup

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="paramkit",
    version="0.2.2",
    author="Dylan",
    author_email="cgq2012516@gmail.com",
    description="A parameter management toolkit for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=["parameters", "configuration", "management"],
    url="https://github.com/Dyaln2012516/paramkit",
    project_urls={
        "Documentation": "https://github.com/Dyaln2012516/paramkit/blob/main/README.md",
        "Issues": "https://github.com/Dyaln2012516/paramkit/issues",
    },
    python_requires=">=3.8",
    packages=find_packages(where="."),
    include_package_data=True,
    package_data={"paramkit": ["docs/static/css/*.css", "docs/static/js/*.js", "docs/static/html/*.html"]},
    install_requires=[
        "typing-extensions>=4.0.0; python_version < '3.8'",
        "peewee >= 3.1.0",
        "mdutils >=1.5.0",
    ],
    extras_require={"test": ["pytest>=7.0", "pytest-cov"], "dev": ["black", "flake8", "mypy", "isort", "pylint", "pycln"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={"console_scripts": ["paramkit = paramkit.cli:main"]},
)
