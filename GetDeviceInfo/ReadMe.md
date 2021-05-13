# Get Device Info
I created this module to gather current state from my Cisco lab equipment.

It uses Nornir with napalm_get/napalm_cli and ntc_templates to retrieve the following information sets:
* general (get_facts)
* interface (get_interfaces)
* ip (get_interfaces_ip)
* vlans (get_vlans)
* interface mode (show interfaces switchport)

This information is then built into a model (Device and Interface classes) and printed using PrettyTable.

# References
* [Nornir](https://nornir.readthedocs.io/en/latest/)
* [Nornir Plugins](https://github.com/nornir-automation/nornir_napalm)
* [Napalm](https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix)
* [ntc_templates](https://github.com/networktocode/ntc-templates)
* [PrettyTable](https://pypi.org/project/prettytable/)
