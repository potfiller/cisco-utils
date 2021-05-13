"""This module collects information from network devices
using nornir and napalm
"""

import os
from datetime import datetime

import yaml
from nornir import InitNornir
from nornir.core.task import Task, Result
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
    table.field_names = ['Interface', 'L2 Addr', 'vlans', 'L3 Addr', 'Mode', 'Enabled', 'Up']
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


def create_model(result) -> list:
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
            for int_name in result[host][1].result['get_interfaces']:

                ### get_interfaces ###
                interface = result[host][1].result['get_interfaces'][int_name]
                new_interface = Interface(
                    name=int_name,
                    l2_addr=interface['mac_address'],
                    vlans = [],
                    l3_addr=[],
                    mode = "",
                    is_enabled=interface['is_enabled'],
                    is_up=interface['is_up']
                )
                #does this interface have an IP record?
                if int_name in result[host][1].result['get_interfaces_ip']:
                    new_interface.mode = "routed"

                    ### get_interfaces_ip ###
                    int_ip = result[host][1].result['get_interfaces_ip'][int_name]['ipv4']
                    for ip_address in int_ip.keys():
                        int_ip_address = ip_address
                        int_ip_prefix = int_ip[ip_address]['prefix_length']
                        new_interface.l3_addr.append(f"{int_ip_address}/{int_ip_prefix}")

                ### get_vlans ###
                vlan_list = result[host][1].result['get_vlans']
                for vlanid in vlan_list.keys():
                    if int_name in vlan_list[vlanid]['interfaces']:
                        new_interface.vlans.append(vlanid)

                ### show interfaces switchport ###
                output_str = result[host][2].result['show interfaces switchport']
                output_parsed = parse_output(
                                    platform="cisco_ios",
                                    command="show interfaces switchport",
                                    data=output_str)
                for entry in output_parsed:
                    #entry['interface'] will be Fa0/1 or similar
                    ent_int = entry['interface']
                    fa_gi = ent_int[0:2]    # Fa
                    int_id = ent_int[2-len(ent_int):]   # 0/1
                    int_mode = entry['mode']
                    if (fa_gi.lower() in int_name.lower()) and (int_id in int_name):
                        new_interface.mode = int_mode

                device.interfaces.append(new_interface)
            devices.append(device)
    return devices


def master_task(task: Task) -> Result:
    """Runs the napalm tasks"""

    task.run(
        task=napalm_get,
        getters=["get_facts", "get_interfaces", "get_interfaces_ip", "get_vlans"]
    )
    task.run(
        task=napalm_cli,
        commands=["show interfaces switchport"]
    )
    return Result(
        host=task.host,
        result=f"{task.host} finished."
    )


def nornir_code(creds: dict):
    """Execute the nornir tasks and process results"""

    # update and filter inventory
    nornir_obj = InitNornir(config_file="config.yaml")
    nornir_obj.inventory.groups["cisco_group"].username = creds['username']
    nornir_obj.inventory.groups["cisco_group"].password = creds['password']

    # # start main task
    # result = nornir_obj.run(
    #     task=napalm_get,
    #     getters=["get_facts", "get_interfaces", "get_interfaces_ip", "get_vlans"]
    # )

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


def setup_creds() -> dict:
    """retrieve credentials"""

    # get credentials
    creds = yaml.safe_load(open('C:\\Users\\Ben\\python\\creds.yaml'))

    return {
        'username': creds['user']['username'],
        'password': creds['user']['password']
    }


def main():
    """app entry point"""

    creds = setup_creds()
    nornir_code(creds)


if __name__ == "__main__":
    main()
