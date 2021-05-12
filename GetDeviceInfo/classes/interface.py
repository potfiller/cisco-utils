from enum import Enum

class IntType(Enum):
    ACCESS = 1
    TRUNK = 2
    ROUTED = 3

class Interface:

    def __init__(self):
        self.name = ""
        self.l2addr = ""
        self.l3addr = ""
        self.int_type = IntType.ACCESS
        self.enabled = False