# use Nornir inventory
# and napalm_get
# to record device hostname, firmware version

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
import yaml
import os
from datetime import datetime

username = ""
password = ""
reportdir = "reports\\"

def write_file(filecontent: str):
    """Write the obtained information to a file
    
    Fields in the file are tab-separated
    File suffix is txt.
    """
    
    #create reports folder
    if not os.path.exists(reportdir):
        os.mkdir(reportdir)
    
    #prepare filename
    datestr = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"inventory_{datestr}.txt"

    #write file
    with open(os.path.join(reportdir, filename), "w") as f:
        f.write(filecontent)

def nornir_code():
    #update and filter inventory
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.groups["cisco_group"].username = username
    nr.inventory.groups["cisco_group"].password = password

    #start main task
    result = nr.run(
        task=napalm_get,
        getters=["get_facts"]
    )

    content = ""
    
    for host in result.keys():
        if not host in result.failed_hosts.keys():
            device = result[host][0].result['get_facts']
            content += f"{device['hostname']}\t{device['model']}\t{device['os_version']}\t{device['serial_number']}\n"
    
    write_file(content)

def setup_creds():
    global username, password
    #get credentials
    creds = yaml.safe_load(open('C:\\Users\\Ben\\python\\creds.yaml'))
    username = creds['user']['username']
    password = creds['user']['password']

def main():
    setup_creds()
    nornir_code()

if __name__ == "__main__":
    main()

