"""The Device class"""

from dataclasses import dataclass

@dataclass
class Device:
    """Information about a network device"""

    hostname: str
    model: str
    os_version: str
    interfaces: list
