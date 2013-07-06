from librtmp_ffi.binding import librtmp
from librtmp_ffi.ffi import C, ffi

from .utils import add_signal_handler

__all__ = ["set_log_level", "get_log_level",
           "set_log_output", "add_log_callback", "remove_log_callback",
           "LOG_CRIT", "LOG_ERROR", "LOG_WARNING",
           "LOG_INFO", "LOG_DEBUG", "LOG_DEBUG2",
           "LOG_ALL"]

(LOG_CRIT, LOG_ERROR, LOG_WARNING, LOG_INFO, LOG_DEBUG,
 LOG_DEBUG2, LOG_ALL) = range(1, 8)

_log_callbacks = set()
_log_level = LOG_ALL
_log_output = None

def set_log_level(level):
    """Sets log level."""

    global _log_level
    _log_level = level

def get_log_level():
    """Returns current log level."""
    return _log_level

def set_log_output(fd):
    """Sets log output to a open file-object."""
    global _log_output
    _log_output = fd

def add_log_callback(callback):
    """Adds a log callback."""
    global _log_callbacks

    if not callable(callback):
        raise ValueError("Callback must be callable")

    _log_callbacks.add(callback)
    return callback

def remove_log_callback(callback):
    """Removes a log callback."""
    global _log_callbacks
    _log_callbacks.remove(callback)

@ffi.callback("RTMP_LogCallback")
def _log_callback(level, fmt, args):
    buf = ffi.new("char[]", 2048)

    C.vsprintf(buf, fmt, args)

    msg = ffi.string(buf)
    msg = msg.decode("utf8", "ignore")

    for callback in _log_callbacks:
        callback(level, msg)

    if hasattr(_log_output, "write") and level <= _log_level:
        _log_output.write(msg + "\n")

librtmp.RTMP_LogSetCallback(_log_callback)
add_signal_handler()

