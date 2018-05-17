from enum import IntEnum, auto


class UART_FSMState(IntEnum):
    """
    Enumerator mapping UART Finite State Machine states to its name.
    """
    Unknown = auto()
    InitDevice = auto()
    Device = auto()
    InitNode = auto()
    Node = auto()
