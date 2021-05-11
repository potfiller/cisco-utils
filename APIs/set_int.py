import requests
import json

# ignore cert errors
requests.packages.urllib3.disable_warnings()

USER = 'developer'
PASS = 'C1sco12345'

# IOS XE on CSR Latest Code Always On Sandbox
# note that the recommended code didn't work!
url = 'https://sandbox-iosxe-latest-1.cisco.com/restconf/data/ietf-interfaces:interfaces'

headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
}

payload = json.dumps({
    "ietf-interfaces:interface": {
        "name": "Loopback66",
        "description": "Added with RESTCONF - Thanks David!",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "6.6.6.6",
                    "netmask": "255.255.255.255"
                }
            ]
        }
    }
})

response = requests.request(
    'POST',
    url,
    auth=(USER, PASS),
    headers=headers,
    data=payload,
    verify=False
)

print('Status Code:' + str(response.status_code))
print('Response Text:' + response.text)
