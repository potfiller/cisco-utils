"""The Interface class"""

from enum import Enum
from dataclasses import dataclass

class IntType(Enum):
    """All ports are one of these"""

    ACCESS = 1
    TRUNK = 2
    ROUTED = 3

@dataclass
class Interface:
    """Information describing an interface"""

    name: str
    l2_addr: str
    l3_addr: str
    int_type: IntType
    enabled: bool
