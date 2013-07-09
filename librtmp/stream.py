from librtmp_ffi.binding import librtmp
from librtmp_ffi.ffi import ffi

from io import IOBase

from .compat import byte_types
from .exceptions import RTMPError

__all__ = ["RTMPStream"]

class RTMPStream(IOBase):
    """A file-like interface to a stream within
       a RTMP session."""

    def __init__(self, client):
        self.client = client
        self._buf = self._view = None
        self._closed = False

    def read(self, size):
        """Attempts to read data from the stream.

        :param size: int, The maximum amount of bytes to read.

        Raises :exc:`IOError` on error.
        """

        if not self._buf or len(self._buf) != size:
            self._buf = ffi.new("char[]", size)
            self._view = ffi.buffer(self._buf, size)

        res = librtmp.RTMP_Read(self.client.rtmp, self._buf, size)

        if res < 0:
            raise IOError("Failed to read data")

        return self._view[:res]

    def write(self, data):
        """Write data to stream.

        :param data: bytes, Data to write to stream

        Raises :exc:`IOError` on error.
        """
        if isinstance(data, bytearray):
            data = bytes(data)

        if not isinstance(data, byte_types):
            raise ValueError("A bytes argument is required")

        res = librtmp.RTMP_Write(self.client.rtmp, data, len(data))

        if res < 0:
            raise IOError("Failed to write data")

        return res

    def pause(self):
        """Pauses the stream."""
        res = librtmp.RTMP_Pause(self.client.rtmp, 1)

        if res < 1:
            raise RTMPError("Failed to pause")

    def unpause(self):
        """Unpauses the stream."""
        res = librtmp.RTMP_Pause(self.client.rtmp, 0)

        if res < 1:
            raise RTMPError("Failed to unpause")

    def seek(self, time):
        """Attempts to seek in the stream.

        :param time: int, Time to seek to in seconds

        """
        res = librtmp.RTMP_SendSeek(self.client.rtmp, time)

        if res < 1:
            raise RTMPError("Failed to seek")

    def close(self):
        """Closes the connection."""
        if not self._closed:
            self._closed = True
            self.client.close()

    @property
    def duration(self):
        """The duration of the stream."""
        return librtmp.RTMP_GetDuration(self.client.rtmp)

