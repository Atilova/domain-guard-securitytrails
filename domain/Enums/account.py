from enum import Enum


class ObtainResultCode(Enum):
    """ObtainCode"""

    UNDEFINED = 'undefined'
    SUCCESS = 'success'
    FAILED = 'failed'
    TIMEOUTED = 'timeouted'