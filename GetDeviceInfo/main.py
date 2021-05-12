"""This module collects information from network devices
using nornir and napalm
"""

import os
from datetime import datetime
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
import yaml
from prettytable import PrettyTable
from classes.device import Device
from classes.interface import Interface, IntType

REPORTDIR = "reports\\"

def write_file(filecontent: str):
    """Write the obtained information to a file

    Fields in the file are tab-separated
    File suffix is txt.
    """

    #create reports folder
    if not os.path.exists(REPORTDIR):
        os.mkdir(REPORTDIR)

    #prepare filename
    datestr = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"inventory_{datestr}.txt"

    #write file
    with open(os.path.join(REPORTDIR, filename), "w") as file_to_write:
        file_to_write.write(filecontent)


def create_device_table(devices: list) -> PrettyTable:
    """Create a PrettyTable from the list of devices"""

    table = PrettyTable()
    table.field_names = ['hostname','model','os_version']
    for device in devices:
        table.add_row([device.hostname, device.model, device.os_version])
    return table


def create_interface_table(device_name: str, interfaces: list) -> PrettyTable:
    """Create a PrettyTable from the list of device interfaces"""

    table = PrettyTable()
    table.field_names = [device_name]
    for interface in interfaces:
        table.add_row([interface.name])
    return table


def create_model(result) -> list:
    """Create a model from the nornir results"""

    devices = []
    for host in result.keys():
        if not host in result.failed_hosts.keys():
            device = Device(
                hostname = result[host][0].result['get_facts']['hostname'],
                model = result[host][0].result['get_facts']['model'],
                os_version = result[host][0].result['get_facts']['os_version'],
                interfaces = []
            )
            for int_name in result[host][0].result['get_facts']['interface_list']:
                device.interfaces.append(
                    Interface(
                        name = int_name,
                        l2_addr = "",
                        l3_addr = "",
                        int_type = IntType.ACCESS,
                        enabled = False
                    )
                )
            devices.append(device)
    return devices


def nornir_code(creds: dict):
    """Execute the nornir tasks and process results"""

    #update and filter inventory
    nornir_obj = InitNornir(config_file="config.yaml")
    nornir_obj.inventory.groups["cisco_group"].username = creds['username']
    nornir_obj.inventory.groups["cisco_group"].password = creds['password']

    #start main task
    result = nornir_obj.run(
        task=napalm_get,
        getters=["get_facts"]
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

    #get credentials
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
