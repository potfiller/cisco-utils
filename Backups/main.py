# use Nornir inventory
# and napalm_get
# to backup device running configs

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
import yaml
import os
from datetime import datetime

username = ""
password = ""
backupdir = "backups\\"

def do_backups(task: Task) -> Result:
    #use napalm to retrieve mac address table
    task.run(
        task=napalm_get,
        getters=["config"]
    )
    return Result(
        host=task.host,
        result=f"{task.host} done."
    )

def run_code():
    #create backup folder
    if not os.path.exists(backupdir):
        os.mkdir(backupdir)

    #get credentials
    creds = yaml.safe_load(open('C:\\Users\\Ben\\python\\creds.yaml'))
    username = creds['user']['username']
    password = creds['user']['password']

    #update and filter inventory
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.groups["cisco_group"].username = username
    nr.inventory.groups["cisco_group"].password = password

    #start main task
    result = nr.run(
        task=do_backups
    )

    datestr = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    
    for host in result.keys():
        filename = f"{host}_{datestr}.cfg"
        config = result[host][1].result['config']['startup']
        with open(os.path.join(backupdir, filename), "w") as f:
            f.write(config)        

def main():
    run_code()

if __name__ == "__main__":
    main()

