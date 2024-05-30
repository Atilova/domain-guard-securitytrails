from enum import Enum, auto


class ProcessStatus(Enum):
    """ProcessStatus"""
    
    PENDING = auto()
    EXECUTING = auto()
    ABORTED = auto()
    CANCELED = auto()
    FAILED = auto()
    DONE = auto()