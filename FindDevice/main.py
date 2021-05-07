# use Nornir inventory
# and napalm_get
# to find where a device is connected

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
import yaml
from classes.Appliance import Appliance

username = ""
password = ""

def mytask(task: Task) -> Result:

    #use napalm to retrieve mac address table
    task.run(
        task=napalm_get,
        getters=["get_mac_address_table","get_interfaces_ip"]
    )
    return Result(
        host=task.host,
        #this sets the task result to the host mac address
        result=''#task.host.data['mac_address']
    )

def run_code():
    #get mac address from user
    mac_address = input("Enter the MAC you are looking for: ")

    #get credentials
    creds = yaml.safe_load(open('C:\\Users\\Ben\\python\\creds.yaml'))
    username = creds['user']['username']
    password = creds['user']['password']

    #update and filter inventory
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.groups["cisco_group"].username = username
    nr.inventory.groups["cisco_group"].password = password
    switches = nr.filter(filter_func=lambda h: "ASW" in h.name)

    #start main task
    result2 = switches.run(
        task=mytask
    )

    # #this bit retrieves a mac from host data
    # asw1_mt = result2["ASW1"][0]
    # print(asw1_mt)
    
    for host in result2.keys():
        for entry in result2[host][1].result['get_mac_address_table']:
            if mac_address in entry['mac']:
                print(f"{host}: {entry['mac']} - {entry['interface']} - vlan{entry['vlan']}")
        



def main():
    run_code()

if __name__ == "__main__":
    main()

