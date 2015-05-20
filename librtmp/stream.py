from io import IOBase

from . import ffi, librtmp
from .compat import byte_types
from .exceptions import RTMPError

__all__ = ["RTMPStream"]


class RTMPStream(IOBase):
    """A file-like interface to a stream within
       a RTMP session."""

    def __init__(self, client, update_buffer=True):
        self.client = client
        self._buf = self._view = None
        self._closed = False
        self._update_buffer = update_buffer
        self._updated_buffer = False

    def read(self, size):
        """Attempts to read data from the stream.

        :param size: int, The maximum amount of bytes to read.

        Raises :exc:`IOError` on error.
        """
        # If enabled tell the server that our buffer can fit the whole
        # stream, this often increases throughput alot.
        if self._update_buffer and not self._updated_buffer and self.duration:
            self.update_buffer((self.duration * 1000) + 5000)
            self._updated_buffer = True

        if not self._buf or len(self._buf) != size:
            self._buf = ffi.new("char[]", size)
            self._view = ffi.buffer(self._buf, size)

        res = librtmp.RTMP_Read(self.client.rtmp, self._buf, size)

        if res < 0:
            raise IOError("Failed to read data")

        return self._view[:res]

    def write(self, data):
        """Writes data to the stream.

        :param data: bytes, FLV data to write to the stream

        The data passed can contain multiple FLV tags, but it MUST
        always contain complete tags or undefined behaviour might
        occur.

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

    def update_buffer(self, ms):
        """Tells the server how big our buffer is (in milliseconds)."""
        librtmp.RTMP_SetBufferMS(self.client.rtmp, int(ms))
        librtmp.RTMP_UpdateBufferMS(self.client.rtmp)

    @property
    def duration(self):
        """The duration of the stream."""
        return librtmp.RTMP_GetDuration(self.client.rtmp)
