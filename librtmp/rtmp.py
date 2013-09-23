from librtmp_ffi.binding import librtmp
from librtmp_ffi.ffi import ffi

from binascii import unhexlify
from collections import defaultdict
from time import time

from .aval import AVal
from .amf import encode_amf, decode_amf, AMFError
from .compat import bytes, string_types, integer_types
from .exceptions import RTMPError, RTMPTimeoutError
from .packet import RTMPPacket, PACKET_TYPE_INVOKE, PACKET_SIZE_MEDIUM
from .stream import RTMPStream
from .utils import hash_swf


__all__ = ["RTMP", "RTMPCall"]

class RTMP(object):
    """ A RTMP client session.

    :param url: str, A RTMP URL in the format `rtmp[t][e|s]://hostname[:port][/app[/playpath]]`.
    :param playpath: str, Overrides the playpath parsed from the RTMP URL.
    :param tcurl: str, URL of the target stream. Defaults to `rtmp[t][e|s]://host[:port]/app`.
    :param app: str, Name of application to connect to on the RTMP server.
    :param pageurl: str, URL of the web page in which the media was embedded.
    :param auth: str, Authentication string to be appended to the connect string.
    :param connect_data: This value will be encoded to AMF and added to the connect packet.
    :param swfhash: str, SHA256 hash of the decompressed SWF file (hexdigest).
    :param swfsize: int, Size of the decompressed SWF file.
    :param swfurl: str, URL of the SWF player for the media.
    :param swfvfy: bool, Calculate the correct swfhash and swfsize parameter
                   from the `swfurl` specified.
    :param flashver: str, Version of the Flash plugin used to run the SWF player.
    :param subscribe: str, Name of live stream to subscribe to. Defaults to `playpath`.
    :param token: str, Key for SecureToken response, used if the server requires
                  SecureToken authentication.
    :param live: bool, Specify that the media is a live stream.
    :param jtv: str, JSON token used by Twitch/Justin.tv servers.
    :param socks: str, Use the specified SOCKS4 proxy.
    :param start: int, Start at num seconds into the stream. Not valid for live streams.
    :param stop: int, Stop at num seconds into the stream.
    :param buffer: int, Set buffer time to num milliseconds. This is used to control
                   rate of data sent by FMS servers, not buffering of data. The default is 30000.
    :param timeout: int, Timeout the session after num seconds without receiving any data
                    from the server. The default is 30.
    """

    def __init__(self, url, playpath=None, tcurl=None, app=None, pageurl=None,
                 auth=None, swfhash=None, swfsize=None, swfurl=None, swfvfy=None,
                 flashver=None, subscribe=None, token=None, live=None, jtv=None,
                 connect_data=None, socks=None, start=None, stop=None, buffer=None,
                 timeout=None):
        def set_opt(key, val):
            if val is not None:
                self.set_option(key, val)

        self.rtmp = librtmp.RTMP_Alloc()

        if self.rtmp == ffi.NULL:
            raise MemoryError("Failed to allocate RTMP handle")

        librtmp.RTMP_Init(self.rtmp)

        self._options = dict()
        self._invoke_args = dict()
        self._invoke_handlers = dict()
        self._invoke_results = dict()
        self._connect_result = None

        self.url = None

        if swfurl and swfvfy:
            swfhash, swfsize = hash_swf(swfurl)

        if swfhash:
            digest = unhexlify(swfhash)
            librtmp.RTMP_SetSWFHash(self.rtmp, digest, swfsize)

        self.setup_url(url)

        set_opt("playpath", playpath)
        set_opt("tcUrl", tcurl)
        set_opt("app", app)

        set_opt("swfUrl", swfurl)
        set_opt("pageUrl", pageurl)
        set_opt("auth", auth)
        set_opt("flashver", flashver)

        set_opt("subscribe", subscribe)
        set_opt("token", token)
        set_opt("jtv", jtv)
        set_opt("live", live)
        set_opt("socks", socks)

        set_opt("start", start)
        set_opt("stop", stop)
        set_opt("buffer", buffer)
        set_opt("timeout", timeout)

        if isinstance(connect_data, (list, tuple)):
            for data in connect_data:
                self._parse_connect_data(data)
        elif connect_data is not None:
            self._parse_connect_data(connect_data)

    def _parse_connect_data(self, val):
        if isinstance(val, bool):
            self.set_option("conn", "B:{0}".format(int(val)))
        elif isinstance(val, string_types):
            self.set_option("conn", "S:{0}".format(val))
        elif isinstance(val, integer_types):
            self.set_option("conn", "N:{0}".format(val))
        elif isinstance(val, type(None)):
            self.set_option("conn", "Z:")
        elif isinstance(val, dict):
            self.set_option("conn", "O:1")
            for key, value in val.items():
                if isinstance(value, bool):
                    self.set_option("conn", "NB:{0}:{1}".format(key, int(value)))
                elif isinstance(value, string_types):
                    self.set_option("conn", "NS:{0}:{1}".format(key, value))
                elif isinstance(value, integer_types):
                    self.set_option("conn", "NN:{0}:{1}".format(key, value))
            self.set_option("conn", "O:0")

    def set_option(self, key, value):
        """Sets a option for this session.

        For a detailed list of available options see the librtmp(3) man page.

        :param key: str, A valid option key.
        :param value: A value, anything that can be converted to str is valid.

        Raises :exc:`ValueError` if a invalid option is specified.

        """

        akey = AVal(key)
        aval = AVal(value)

        res = librtmp.RTMP_SetOpt(self.rtmp, akey.aval, aval.aval)

        if res < 1:
            raise ValueError("Unable to set option {0}".format(key))

        self._options[akey] = aval

    def setup_url(self, url):
        r"""Attempt to parse a RTMP URL.

        Additional options may be specified by appending space-separated
        key=value pairs to the URL. Special characters in values may need
        to be escaped to prevent misinterpretation by the option parser.
        The escape encoding uses a backslash followed by two hexadecimal
        digits representing the ASCII value of the character. E.g., spaces
        must be escaped as `\\20` and backslashes must be escaped as `\\5c`.

        :param url: str, A RTMP URL in the format `rtmp[t][e|s]://hostname[:port][/app[/playpath]]`

        Raises :exc:`RTMPError` if URL parsing fails.

        """

        self.url = bytes(url, "utf8")

        res = librtmp.RTMP_SetupURL(self.rtmp, self.url)
        if res < 1:
            raise RTMPError("Unable to parse URL")

    def connect(self, packet=None):
        """Connect to the server.

        :param packet: RTMPPacket, this packet will be sent instead
                       of the regular "connect" packet.

        Raises :exc:`RTMPError` if the connect attempt fails.

        """

        if isinstance(packet, RTMPPacket):
            packet = packet.packet
        else:
            packet = ffi.NULL

        res = librtmp.RTMP_Connect(self.rtmp, packet)
        if res < 1:
            raise RTMPError("Failed to connect")

        return RTMPCall(self, 1.0)

    def create_stream(self, seek=None, writeable=False):
        """Prepares the session for streaming of audio/video
           and returns a :class:`RTMPStream` object.

        :param seek: int, Attempt to seek to this position.
        :param writeable: bool, Make the stream writeable instead of readable.

        Raises :exc:`RTMPError` if a stream could not be created.

        Usage::

          >>> stream = conn.create_stream()
          >>> data = stream.read(1024)
        """

        if writeable:
            librtmp.RTMP_EnableWrite(self.rtmp)

        # Calling handle_packet() on a connect result causes
        # librtmp to send a CreateStream call. This is not always
        # desired when using process_packets(), therefore we do it
        # here instead.
        if self._connect_result:
            self.handle_packet(self._connect_result)

        if not seek:
            seek = 0

        res = librtmp.RTMP_ConnectStream(self.rtmp, seek)
        if res < 1:
            raise RTMPError("Failed to start RTMP playback")

        return RTMPStream(self)

    @property
    def connected(self):
        """Returns True if connected to the server.

        Usage::

          >>> conn.connected
          True
        """

        return bool(librtmp.RTMP_IsConnected(self.rtmp))

    def read_packet(self):
        """Reads a RTMP packet from the server.

        Returns a :class:`RTMPPacket`.

        Raises :exc:`RTMPError` on error.
        Raises :exc:`RTMPTimeoutError` on timeout.

        Usage::

          >>> packet = conn.read_packet()
          >>> packet.body
          b'packet body ...'
        """

        packet = ffi.new("RTMPPacket*")
        packet_complete = False

        while not packet_complete:
            res = librtmp.RTMP_ReadPacket(self.rtmp, packet)

            if res < 1:
                if librtmp.RTMP_IsTimedout(self.rtmp):
                    raise RTMPTimeoutError("Timed out while reading packet")
                else:
                    raise RTMPError("Failed to read packet")

            packet_complete = packet.m_nBytesRead == packet.m_nBodySize

        return RTMPPacket._from_pointer(packet)

    def send_packet(self, packet, queue=True):
        """Sends a RTMP packet to the server.

        :param packet: RTMPPacket, the packet to send to the server.
        :param queue: bool, If True, queue up the packet in a internal queue rather
                      than sending it right away.

        """

        if not isinstance(packet, RTMPPacket):
            raise ValueError("A RTMPPacket argument is required")

        return librtmp.RTMP_SendPacket(self.rtmp, packet.packet,
                                       int(queue))

    def handle_packet(self, packet):
        """Lets librtmp look at a packet and send a response
           if needed."""

        if not isinstance(packet, RTMPPacket):
            raise ValueError("A RTMPPacket argument is required")

        return librtmp.RTMP_ClientPacket(self.rtmp, packet.packet)

    def process_packets(self, transaction_id=None, invoked_method=None,
                        timeout=None):
        """Wait for packets and process them as needed.

        :param transaction_id: int, Wait until the result of this
                               transaction ID is recieved.
        :param invoked_method: int, Wait until this method is invoked
                               by the server.
        :param timeout: int, The time to wait for a result from the server.
                             Note: This is the timeout used by this method only,
                             the connection timeout is still used when reading
                             packets.

        Raises :exc:`RTMPError` on error.
        Raises :exc:`RTMPTimeoutError` on timeout.

        Usage::

          >>> @conn.invoke_handler
          ... def add(x, y):
          ...   return x + y

          >>> @conn.process_packets()

        """

        start = time()

        while self.connected and transaction_id not in self._invoke_results:
            if timeout and (time() - start) >= timeout:
                raise RTMPTimeoutError("Timeout")

            packet = self.read_packet()

            if packet.type == PACKET_TYPE_INVOKE:
                try:
                    decoded = decode_amf(packet.body)
                except AMFError:
                    continue

                try:
                    method, transaction_id_, obj = decoded[:3]
                    args = decoded[3:]
                except ValueError:
                    continue

                if method == "_result":
                    if len(args) > 0:
                        result = args[0]
                    else:
                        result = None

                    self._invoke_results[transaction_id_] = result
                else:
                    handler = self._invoke_handlers.get(method)
                    if handler:
                        res = handler(*args)
                        if res is not None:
                            self.call("_result", res,
                                      transaction_id=transaction_id_)

                    if method == invoked_method:
                        self._invoke_args[invoked_method] = args
                        break

                if transaction_id_ == 1.0:
                    self._connect_result = packet
                else:
                    self.handle_packet(packet)
            else:
                self.handle_packet(packet)

        if transaction_id:
            result = self._invoke_results.pop(transaction_id, None)

            return result

        if invoked_method:
            args = self._invoke_args.pop(invoked_method, None)

            return args

    def call(self, method, *args, **params):
        """Calls a method on the server."""

        transaction_id = params.get("transaction_id")

        if not transaction_id:
            self.transaction_id += 1
            transaction_id = self.transaction_id

        obj = params.get("obj")

        args = [method, transaction_id, obj] + list(args)
        args_encoded = map(lambda x: encode_amf(x), args)
        body = b"".join(args_encoded)

        format = params.get("format", PACKET_SIZE_MEDIUM)
        channel = params.get("channel", 0x03)

        packet = RTMPPacket(type=PACKET_TYPE_INVOKE,
                            format=format, channel=channel,
                            body=body)

        self.send_packet(packet)

        return RTMPCall(self, transaction_id)

    def remote_method(self, method, block=False, **params):
        """Creates a Python function that will attempt to
           call a remote method when used.

        :param method: str, Method name on the server to call
        :param block: bool, Wheter to wait for result or not

        Usage::

          >>> send_usher_token = conn.remote_method("NetStream.Authenticate.UsherToken", block=True)
          >>> send_usher_token("some token")
          'Token Accepted'
        """

        def func(*args):
            call = self.call(method, *args, **params)

            if block:
                return call.result()

            return call

        func.__name__ = method

        return func

    def invoke_handler(self, func=None, name=None):
        if not callable(func):
            return lambda f: self.invoke_handler(func=f, name=func)

        method = name or func.__name__
        self.register_invoke_handler(method, func)

        return func

    def register_invoke_handler(self, method, func):
        self._invoke_handlers[method] = func

    def close(self):
        """Closes the connection to the server."""
        if self.connected:
            librtmp.RTMP_Close(self.rtmp)

    @property
    def transaction_id(self):
        return librtmp.RTMP_GetInvokeCount(self.rtmp)

    @transaction_id.setter
    def transaction_id(self, val):
        librtmp.RTMP_SetInvokeCount(self.rtmp, int(val))

    def __del__(self):
        librtmp.RTMP_Free(self.rtmp)


class RTMPCall(object):
    """A RTMP call.

    Contains the result of a :meth:`RTMP.call`.
    """

    def __init__(self, conn, transaction_id):
        self._result = None

        self.conn = conn
        self.done = False
        self.transaction_id = transaction_id

    def result(self, timeout=None):
        """Retrieves the result of the call.

        :param timeout: The time to wait for a result from the server.

        Raises :exc:`RTMPTimeoutError` on timeout.
        """
        if self.done:
            return self._result

        result = self.conn.process_packets(transaction_id=self.transaction_id,
                                           timeout=timeout)

        self._result = result
        self.done = True

        return result

