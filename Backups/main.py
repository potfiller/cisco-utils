""""use Nornir inventory
and napalm_get to backup devices' running configs
"""

import os
from datetime import datetime

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
import yaml

BACKUPDIR = "backups\\"


def do_backups(task: Task) -> Result:
    """Runs the napalm tasks"""

    task.run(
        task=napalm_get,
        getters=["config"]
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

    # ensure there is a directory for the backup files
    if not os.path.exists(BACKUPDIR):
        os.mkdir(BACKUPDIR)

    # prepare a timetime string for the filenames
    datestr = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")

    # get the login credentials
    creds = setup_creds()

    # update and filter inventory
    nornir_obj = InitNornir(config_file="config.yaml")
    nornir_obj.inventory.groups["cisco_group"].username = creds['username']
    nornir_obj.inventory.groups["cisco_group"].password = creds['password']

    # start main task
    result = nornir_obj.run(
        task=do_backups
    )

    if len(result.keys()) > len(result.failed_hosts.keys()):
        for host in result.keys():
            filename = f"{host}_{datestr}.cfg"
            config = result[host][1].result['config']['startup']
            with open(os.path.join(BACKUPDIR, filename), "w") as backup_file:
                backup_file.write(config)


if __name__ == "__main__":
    main()
