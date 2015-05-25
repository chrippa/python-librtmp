#!/usr/bin/env python
from setuptools import setup
from sys import version_info


install_requires = ["cffi>=1.0.1"]

if not (version_info[0] == 3 and version_info[1] >= 4):
    install_requires.append("singledispatch")

readme = open("README.rst").read()
history = open("HISTORY.rst").read().replace(".. :changelog:", "")

setup(
    name="python-librtmp",
    version="0.3.0",
    description="Python bindings for librtmp, built with cffi",
    long_description=readme + "\n\n" + history,
    author="Christopher Rosell",
    author_email="chrippa@tanuki.se",
    url="https://github.com/chrippa/python-librtmp",
    license="Simplified BSD",
    packages=["librtmp"],
    cffi_modules=["librtmp/ffi.py:ffi"],
    install_requires=install_requires,
    setup_requires=["cffi>=1.0.1"],
    zip_safe=False,
    keywords="python-librtmp",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ]
)
