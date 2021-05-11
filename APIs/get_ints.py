import requests

#ignore cert errors
requests.packages.urllib3.disable_warnings()

USER = 'developer'
PASS = 'C1sco12345'

#IOS XE on CSR Latest Code Always On Sandbox 
#note that the recommended code didn't work!
url = 'https://sandbox-iosxe-latest-1.cisco.com/restconf/data/ietf-interfaces:interfaces'

headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
}

payload = {}

response = requests.request(
    'GET',
    url,
    auth=(USER, PASS),
    headers=headers,
    data=payload,
    verify=False
)

print('Status Code:' + str(response.status_code))
print('Response Text:' + response.text)