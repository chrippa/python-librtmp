#!/usr/bin/env python

try:
    raise ImportError
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from sys import version_info

# First attempt to generate extension source with cffi,
# then fallback to already generated source.
try:
    from librtmp_ffi.verifier import verifier
    extension = verifier.get_extension()
except ImportError:
    from distutils.extension import Extension
    extension = Extension("_binding", ["librtmp_ffi/__pycache__/_binding.c"],
                          libraries=["rtmp"])

install_requires = ["cffi>=0.6"]

if not (version_info[0] == 3 and version_info[1] > 4):
    install_requires.append("singledispatch")

readme = open("README.rst").read()
history = open("HISTORY.rst").read().replace(".. :changelog:", "")

setup(name="python-librtmp",
      version="0.1.0",
      description="Python bindings for librtmp, built with cffi",
      long_description=readme + "\n\n" + history,
      author="Christopher Rosell",
      author_email="chrippa@tanuki.se",
      url="https://github.com/chrippa/python-librtmp",
      license="Simplified BSD",
      packages=["librtmp", "librtmp_config", "librtmp_ffi"],
      install_requires=install_requires,
      zip_safe=False,
      keywords="python-librtmp",
      ext_package="librtmp_ffi",
      ext_modules=[extension],
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
      ]
)
