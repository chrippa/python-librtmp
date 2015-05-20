from . import ffi
from .compat import bytes, integer_types, string_types


__all__ = ["AVal"]


class AVal(object):
    def __init__(self, value=None):
        self.aval = ffi.new("AVal *")

        if value is not None:
            self.value = value

    @property
    def value(self):
        buf = ffi.buffer(self.aval.av_val, self.aval.av_len)
        return buf[:]

    @value.setter
    def value(self, value):
        if isinstance(value, integer_types):
            value = str(value)
        if isinstance(value, string_types):
            value = bytes(value, "utf8")
        elif isinstance(value, bool):
            value = str(value).lower()

        self.value_str = ffi.new("char[]", value)
        self.aval.av_val = self.value_str
        self.aval.av_len = len(value)
