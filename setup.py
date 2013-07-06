#!/usr/bin/env python

from setuptools import setup
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

setup(name="python-librtmp",
      version="0.1.0",
      description="Python bindings for librtmp, built with cffi",
      url="https://github.com/chrippa/python-librtmp",
      author="Christopher Rosell",
      author_email="chrippa@tanuki.se",
      license="Simplified BSD",
      packages=["librtmp", "librtmp_config", "librtmp_ffi"],
      install_requires=install_requires,
      zip_safe=False,
      ext_package="librtmp_ffi",
      ext_modules=[extension]
)
