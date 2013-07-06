from librtmp_ffi.binding import librtmp
from librtmp_ffi.ffi import ffi

from binascii import hexlify
from collections import namedtuple

from .aval import AVal
from .compat import bytes, str
from .exceptions import RTMPError

__all__ = ["add_signal_handler", "hash_swf"]

def add_signal_handler():
    """Adds a signal handler to handle KeyboardInterrupt."""
    import signal

    def handler(sig, frame):
        if sig == signal.SIGINT:
            librtmp.RTMP_UserInterrupt()
            raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handler)

def hash_swf(url, age=30):
    hash = ffi.new("unsigned char[]", 32)
    size = ffi.new("unsigned int*")
    url = bytes(url, "utf8")

    res = librtmp.RTMP_HashSWF(url, size, hash, age)

    if res == 0:
        hash = hexlify(ffi.buffer(hash, 32)[:])
        size = size[0]

        return str(hash, "utf8"), size
    else:
        raise RTMPError("Failed to hash SWF")


RTMPURL = namedtuple("RTMPURL", ["protocol", "hostname",
                     "port", "playpath", "app"])

def parse_url(url):
    protocol = ffi.new("int*")
    hostname = AVal("")
    port = ffi.new("unsigned int*")
    playpath = AVal("")
    app = AVal("")

    res = librtmp.RTMP_ParseURL(bytes(url, "utf8"), protocol, hostname.aval, port,
                                playpath.aval, app.aval)

    if res < 1:
        result = RTMPURL(0, "", 0, "", "")
    else:
        result = RTMPURL(protocol[0], str(hostname.value, "utf8"), port[0],
                         str(playpath.value, "utf8"), str(app.value, "utf8"))

    return result
