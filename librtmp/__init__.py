"""Python bindings for librtmp, built with cffi."""

from .compat import is_win32

if is_win32:
    import socket # Import socket to initialize WinSock

from ._librtmp import ffi, lib as librtmp

librtmp_version = librtmp.RTMP_LibVersion()

if librtmp_version < 0x020300:
    raise ImportError("Only librtmp version >= 2.3 is supported by this library")

from .exceptions import RTMPError, RTMPTimeoutError
from .logging import *
from .packet import *
from .rtmp import *
from .stream import *
from .utils import *

__title__ = "python-librtmp"
__version__ = "0.3.0"
__license__ = "Simplified BSD"
__author__ = "Christopher Rosell"
__copyright__ = "Copyright 2013-2015 Christopher Rosell"
