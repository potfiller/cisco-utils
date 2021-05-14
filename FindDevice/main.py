"""use Nornir inventory and napalm_get
to find where a device is connected
"""

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
import yaml


def get_address_info(task: Task) -> Result:
    """Retrieve L2 address info"""

    #use napalm to retrieve mac address table
    task.run(
        task=napalm_get,
        getters=["get_mac_address_table"]
    )
    return Result(
        host=task.host,
        result=f"{task.host} done."
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
    """Main function"""

    #get mac address from user
    mac_address = input("Enter the MAC you are looking for: ")

    creds = setup_creds()

    #update and filter inventory
    nornir_obj = InitNornir(config_file="config.yaml")
    nornir_obj.inventory.groups["cisco_group"].username = creds['username']
    nornir_obj.inventory.groups["cisco_group"].password = creds['password']

    #start main task
    result = nornir_obj.run(
        task=get_address_info
    )

    if len(result.keys()) > len(result.failed_hosts.keys()):
        for host in result.keys():
            for entry in result[host][1].result['get_mac_address_table']:
                if mac_address in entry['mac']:
                    print(f"{host}: {entry['mac']} - {entry['interface']} - vlan{entry['vlan']}")


if __name__ == "__main__":
    main()
