import librtmp_config

from .ffi import ffi
from .verifier import verifier

for path in librtmp_config.library_paths:
    try:
        librtmp = ffi.dlopen(path)
        break
    except OSError:
        pass
else:
    raise ImportError("No shared library could be loaded, "
                      "make sure that librtmp is installed.")

librtmp = verifier.load_library()
