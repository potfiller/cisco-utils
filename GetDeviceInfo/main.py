"""This module collects information from network devices
using nornir and napalm
"""

import os
from datetime import datetime

import yaml
from nornir import InitNornir
from nornir.core.task import AggregatedResult, Task, Result
from nornir_napalm.plugins.tasks import napalm_get, napalm_cli
from prettytable import PrettyTable
from ntc_templates.parse import parse_output

from classes.device import Device
from classes.interface import Interface

REPORTDIR = "reports\\"


def write_file(filecontent: str):
    """Write the obtained information to a file

    Fields in the file are tab-separated
    File suffix is txt.
    """

    # create reports folder
    if not os.path.exists(REPORTDIR):
        os.mkdir(REPORTDIR)

    # prepare filename
    datestr = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"inventory_{datestr}.txt"

    # write file
    with open(os.path.join(REPORTDIR, filename), "w") as file_to_write:
        file_to_write.write(filecontent)


def create_interface_table(device_name: str, interfaces: list) -> PrettyTable:
    """Create a PrettyTable from the list of device interfaces"""

    table = PrettyTable()
    table.title = device_name
    table.field_names = ['Interface', 'L2 Addr',
                         'vlans', 'L3 Addr', 'Mode', 'Enabled', 'Up']
    for interface in interfaces:
        table.add_row([
            interface.name,
            interface.l2_addr,
            interface.vlans_str(),
            interface.l3_addr_str(),
            interface.mode,
            interface.is_enabled,
            interface.is_up])
    return table


def create_device_table(devices: list) -> PrettyTable:
    """Create a PrettyTable from the list of devices"""

    table = PrettyTable()
    table.field_names = ['hostname', 'model', 'os_version']
    for device in devices:
        table.add_row([device.hostname, device.model, device.os_version])
    return table


def get_int_mode(host: str, int_name: str, result: AggregatedResult) -> str:
    """Get the mode(static, trunk, down) for an interface"""

    mode = ""
    ### show interfaces switchport ###
    output_parsed = parse_output(
        platform="cisco_ios",
        command="show interfaces switchport",
        data=result[host][2].result['show interfaces switchport']
    )
    for entry in output_parsed:
        # entry['interface'] will be Fa0/1 or similar
        ent_int = entry['interface']
        fa_gi = ent_int[0:2]    # Fa
        int_id = ent_int[2-len(ent_int):]   # 0/1
        int_mode = entry['mode']
        if (fa_gi.lower() in int_name.lower()) and (int_id in int_name):
            mode = int_mode

    return mode


def build_vlans(host: str, int_name: str,  result: AggregatedResult) -> list:
    """Build a list of vlans for an interface and host"""

    vlan_ids = []
    vlan_list = result[host][1].result['get_vlans']
    for vlanid in vlan_list.keys():
        if int_name in vlan_list[vlanid]['interfaces']:
            vlan_ids.append(vlanid)

    return vlan_ids


def build_interfaces(host: str, result: AggregatedResult) -> list:
    """Build a list of interfaces for the host"""

    interfaces = []  # list[Interface]
    for int_name in result[host][1].result['get_interfaces']:

        ### get_interfaces ###
        interface = result[host][1].result['get_interfaces'][int_name]
        new_interface = Interface(
            name=int_name,
            l2_addr=interface['mac_address'],
            vlans=[],
            l3_addr=[],
            mode="",
            is_enabled=interface['is_enabled'],
            is_up=interface['is_up']
        )
        # does this interface have an IP record?
        if int_name in result[host][1].result['get_interfaces_ip']:
            new_interface.mode = "routed"

            ### get_interfaces_ip ###
            int_ip = result[host][1].result['get_interfaces_ip'][int_name]['ipv4']
            for ip_address in int_ip.keys():
                int_ip_address = ip_address
                int_ip_prefix = int_ip[ip_address]['prefix_length']
                new_interface.l3_addr.append(
                    f"{int_ip_address}/{int_ip_prefix}")

        new_interface.vlans = build_vlans(host, int_name, result)

        #check the mode for L2 ports
        if new_interface.l3_addr_str() == "":
            new_interface.mode = get_int_mode(host, int_name, result)

        interfaces.append(new_interface)

    return interfaces


def create_model(result: AggregatedResult) -> list:
    """Create a list of devices from the nornir results"""

    devices = []    # list[Device]
    for host in result.keys():
        if not host in result.failed_hosts.keys():
            device = Device(
                hostname=result[host][1].result['get_facts']['hostname'],
                model=result[host][1].result['get_facts']['model'],
                os_version=result[host][1].result['get_facts']['os_version'],
                interfaces=[]
            )
            device.interfaces = build_interfaces(host, result)
            devices.append(device)

    return devices


def master_task(task: Task) -> Result:
    """Runs the napalm tasks"""

    task.run(
        task=napalm_get,
        getters=["get_facts", "get_interfaces",
                 "get_interfaces_ip", "get_vlans"]
    )
    task.run(
        task=napalm_cli,
        commands=["show interfaces switchport"]
    )
    return Result(
        host=task.host,
        result=f"{task.host} finished."
    )


def setup_creds() -> dict:
    """retrieve credentials"""

    # get credentials
    creds = yaml.safe_load(open('C:\\Users\\Ben\\python\\creds.yaml'))

    return {
        'username': creds['user']['username'],
        'password': creds['user']['password']
    }


def main():
    """Execute the nornir tasks and process results"""

    creds = setup_creds()

    # update and filter inventory
    nornir_obj = InitNornir(config_file="config.yaml")
    nornir_obj.inventory.groups["cisco_group"].username = creds['username']
    nornir_obj.inventory.groups["cisco_group"].password = creds['password']

    result = nornir_obj.run(
        task=master_task
    )

    devices = create_model(result)
    device_content = ""
    device_table = create_device_table(devices)
    print(device_table)

    for device in devices:
        device_content += f"{device.hostname}\t{device.model}\t{device.os_version}\n"
        int_table = create_interface_table(device.hostname, device.interfaces)
        print(int_table)

    write_file(device_content)


if __name__ == "__main__":
    main()
