from librtmp_ffi.binding import librtmp
from librtmp_ffi.ffi import ffi

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

from .aval import AVal
from .compat import is_py2, bytes, range
from .exceptions import AMFError

AMF_STRING_TYPES = (librtmp.AMF_STRING, librtmp.AMF_LONG_STRING)
AMF_OBJECT_DICT_TYPES = (librtmp.AMF_OBJECT, librtmp.AMF_ECMA_ARRAY)

__all__ = ["AMFObject", "decode_amf", "encode_amf"]

class AMFObject(dict):
    pass

def _create_buffer(size):
    pbuf = ffi.new("char[]", size)
    pend = pbuf + size
    buf = ffi.buffer(pbuf, size)

    return pbuf, pend, buf

def _encode_key_name(key):
    key = bytes(key, "utf8")
    key_len = len(key)

    pbuf, pend, buf = _create_buffer(key_len + 2)

    librtmp.AMF_EncodeInt16(pbuf, pend, key_len)
    buf[2:key_len + 2] = key

    return buf[:]


@singledispatch
def encoder(val):
    raise AMFError("Unable to encode '{0}' type".format(type(val).__name__))


@encoder.register(type(None))
def _encode_none(val):
    return bytes((librtmp.AMF_NULL,))

@encoder.register(str)
def _encode_str(val):
    val = AVal(val)
    pbuf, pend, buf = _create_buffer(val.aval.av_len + 1 + 4)

    res = librtmp.AMF_EncodeString(pbuf, pend, val.aval)
    size = res - pbuf

    return buf[:size]

if is_py2:
    encoder.register(unicode, _encode_str)


@encoder.register(float)
@encoder.register(int)
def _encode_number(val):
    val = float(val)
    pbuf, pend, buf = _create_buffer(9)

    librtmp.AMF_EncodeNumber(pbuf, pend, val)

    return buf[:]

if is_py2:
    encoder.register(long, _encode_number)


@encoder.register(bool)
def _encode_boolean(val):
    pbuf, pend, buf = _create_buffer(2)
    librtmp.AMF_EncodeBoolean(pbuf, pend, int(val))

    return buf[:]


@encoder.register(AMFObject)
def _encode_object(val):
    phead, headend, head = _create_buffer(4)
    head[0] = bytes((librtmp.AMF_OBJECT,))
    librtmp.AMF_EncodeInt24(phead + 1, headend, librtmp.AMF_OBJECT_END)

    body = bytearray()

    for key, value in val.items():
        body += _encode_key_name(key)
        body += encoder(value)

    return head[:1] + bytes(body) + head[1:]

@encoder.register(dict)
def _encode_ecma_array(val):
    phead, headend, head = _create_buffer(8)
    head[0] = bytes((librtmp.AMF_ECMA_ARRAY,))
    librtmp.AMF_EncodeInt32(phead + 1 , headend, len(val))
    librtmp.AMF_EncodeInt24(phead + 5, headend, librtmp.AMF_OBJECT_END)

    body = bytearray()

    for key, value in val.items():
        body += _encode_key_name(key)
        body += encoder(value)

    return head[:5] + bytes(body) + head[5:]


@encoder.register(list)
def _encode_array(val):
    phead, headend, head = _create_buffer(5)
    head[0] = bytes((librtmp.AMF_STRICT_ARRAY,))
    librtmp.AMF_EncodeInt32(phead + 1, headend, len(val))

    body = bytearray()

    for value in val:
        body += encoder(value)

    return head[:] + bytes(body)


def _decode_prop(prop):
    prop_type = librtmp.AMFProp_GetType(prop)

    if prop_type == librtmp.AMF_NUMBER:
        val = librtmp.AMFProp_GetNumber(prop)
    elif prop_type in AMF_STRING_TYPES:
        aval = AVal()
        librtmp.AMFProp_GetString(prop, aval.aval)
        val = aval.value.decode("utf8", "ignore")
    elif prop_type == librtmp.AMF_BOOLEAN:
        val = bool(librtmp.AMFProp_GetBoolean(prop))
    elif prop_type in AMF_OBJECT_DICT_TYPES:
        if prop_type == librtmp.AMF_OBJECT:
            val = AMFObject()
        else:
            val = dict()

        for key, value in _decode_prop_obj(prop):
            val[key] = value
    elif prop_type == librtmp.AMF_STRICT_ARRAY:
        val = []
        for key, value in _decode_prop_obj(prop):
            val.append(value)
    else:
        val = None

    return val

def _decode_prop_obj(prop):
    obj = ffi.new("AMFObject*")
    librtmp.AMFProp_GetObject(prop, obj)

    prop_count = librtmp.AMF_CountProp(obj)

    for i in range(prop_count):
        prop = librtmp.AMF_GetProp(obj, ffi.NULL, i)

        key = AVal()
        librtmp.AMFProp_GetName(prop, key.aval)
        key = key.value.decode("utf8", "ignore")

        value = _decode_prop(prop)

        yield key, value


def encode_amf(value):
    return encoder(value)

def decode_amf(body):
    obj = ffi.new("AMFObject*")
    res = librtmp.AMF_Decode(obj, body, len(body), 0)

    if res == ffi.NULL:
        raise AMFError("Unable to decode AMF data")

    rval = []
    prop_count = librtmp.AMF_CountProp(obj)

    for i in range(prop_count):
        prop = librtmp.AMF_GetProp(obj, ffi.NULL, i)
        val = _decode_prop(prop)
        rval.append(val)

    return rval
