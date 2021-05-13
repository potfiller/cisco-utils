"""The Interface class"""

from dataclasses import dataclass

@dataclass
class Interface:
    """Information describing an interface"""

    name: str
    l2_addr: str
    l3_addr: list
    vlans: list
    mode: str
    is_enabled: bool
    is_up: bool


    def l3_addr_str(self) -> str:
        """Return the L3 address as str list"""

        addr_str = ""
        if len(self.l3_addr) > 0:
            for address in self.l3_addr:
                addr_str += f"{address}\n"
            strend = len(addr_str)-1
            addr_str = addr_str[0: strend]
        return addr_str


    def vlans_str(self) -> str:
        """Return the vlans as str list"""

        vlans_str = ""
        if len(self.vlans) > 0:
            for vlan in self.vlans:
                vlans_str += f"{vlan}\n"
            strend = len(vlans_str)-1
            vlans_str = vlans_str[0: strend]
        return vlans_str
