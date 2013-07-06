from librtmp_ffi.binding import librtmp
from librtmp_ffi.ffi import ffi

__all__ = ["RTMPPacket",
           "PACKET_SIZE_LARGE", "PACKET_SIZE_MEDIUM",
           "PACKET_SIZE_SMALL", "PACKET_SIZE_MINIMUM",

           "PACKET_TYPE_CHUNK_SIZE", "PACKET_TYPE_BYTES_READ_REPORT",
           "PACKET_TYPE_CONTROL", "PACKET_TYPE_SERVER_BW",
           "PACKET_TYPE_CLIENT_BW", "PACKET_TYPE_AUDIO",
           "PACKET_TYPE_VIDEO", "PACKET_TYPE_FLEX_STREAM_SEND",
           "PACKET_TYPE_FLEX_SHARED_OBJECT", "PACKET_TYPE_FLEX_MESSAGE",
           "PACKET_TYPE_INFO", "PACKET_TYPE_SHARED_OBJECT",
           "PACKET_TYPE_INVOKE", "PACKET_TYPE_FLASH_VIDEO"]


(PACKET_SIZE_LARGE, PACKET_SIZE_MEDIUM, PACKET_SIZE_SMALL,
 PACKET_SIZE_MINIMUM) = range(4)

PACKET_TYPE_CHUNK_SIZE         = 0x01
PACKET_TYPE_BYTES_READ_REPORT  = 0x03
PACKET_TYPE_CONTROL            = 0x04
PACKET_TYPE_SERVER_BW          = 0x05
PACKET_TYPE_CLIENT_BW          = 0x06
PACKET_TYPE_AUDIO              = 0x08
PACKET_TYPE_VIDEO              = 0x09
PACKET_TYPE_FLEX_STREAM_SEND   = 0x0F
PACKET_TYPE_FLEX_SHARED_OBJECT = 0x10
PACKET_TYPE_FLEX_MESSAGE       = 0x11
PACKET_TYPE_INFO               = 0x12
PACKET_TYPE_SHARED_OBJECT      = 0x13
PACKET_TYPE_INVOKE             = 0x14
PACKET_TYPE_FLASH_VIDEO        = 0x16


class RTMPPacket(object):
    @classmethod
    def _from_pointer(cls, pointer):
        packet = cls.__new__(cls)
        packet.packet = pointer

        return packet

    def __init__(self, type, format, channel, timestamp=0,
                 absolute_timestamp=False, body=None):
        self.packet = ffi.new("RTMPPacket*")
        self.type = type
        self.format = format
        self.channel = channel
        self.timestamp = timestamp
        self.absolute_timestamp = absolute_timestamp

        if not body:
            body = b""

        self.body = body

    @property
    def format(self):
        """Format of the packet."""
        return self.packet.m_headerType

    @format.setter
    def format(self, value):
        self.packet.m_headerType = int(value)

    @property
    def type(self):
        """Type of the packet."""
        return self.packet.m_packetType

    @type.setter
    def type(self, value):
        self.packet.m_packetType = int(value)

    @property
    def channel(self):
        """Channel of the packet."""
        return self.packet.m_nChannel

    @channel.setter
    def channel(self, value):
        self.packet.m_nChannel = int(value)

    @property
    def timestamp(self):
        """Timestamp of the packet."""
        return self.packet.m_nTimeStamp

    @timestamp.setter
    def timestamp(self, value):
        self.packet.m_nTimeStamp = int(value)

    @property
    def absolute_timestamp(self):
        """True if the timestamp is absolute."""
        return bool(self.packet.m_hasAbsTimestamp)

    @absolute_timestamp.setter
    def absolute_timestamp(self, value):
        self.packet.m_hasAbsTimestamp = int(bool(value))

    @property
    def body(self):
        """The body of the packet."""
        view = ffi.buffer(self.packet.m_body, self.packet.m_nBodySize)

        return view[:]

    @body.setter
    def body(self, value):
        size = len(value)
        librtmp.RTMPPacket_Alloc(self.packet, size)

        view = ffi.buffer(self.packet.m_body, size)
        view[:] = value

        self.packet.m_nBodySize = size

    def dump(self):
        """Dumps packet to logger."""
        librtmp.RTMPPacket_Dump(self.packet)

    def __del__(self):
        librtmp.RTMPPacket_Free(self.packet)

