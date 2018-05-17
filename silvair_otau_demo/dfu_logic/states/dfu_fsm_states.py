from enum import Enum, auto


class DFUState(Enum):
    """
    Enumerator mapping DFU Finite State Machine states to its name.
    """
    Standby = auto()
    Upload = auto()
    UploadPage = auto()
