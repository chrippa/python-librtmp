__all__ = ["AMFError", "RTMPError", "RTMPTimeoutError"]

class AMFError(Exception):
    pass

class RTMPError(Exception):
    pass

class RTMPTimeoutError(RTMPError):
    pass

