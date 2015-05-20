__all__ = ["AMFError", "RTMPError", "RTMPTimeoutError"]


class AMFError(Exception):
    pass


class RTMPError(IOError):
    pass


class RTMPTimeoutError(RTMPError):
    pass
