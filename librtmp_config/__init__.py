"""Runtime configuration of python-librtmp.

   This module provides access to variables used by this library
   and makes it possible to customize some behaviour before :mod:`librtmp`
   is imported.

"""


__all__ = ["library_paths"]


#: This is a list of filenames that python-librtmp
#: will attempt to dynamically load `librtmp` from.
library_paths = ["librtmp.so", "librtmp.so.0", "librtmp.dll"]
