import requests
import json

# url="https://api.instatus.com/v2/pages?page=:page&per_page=:per_page" # status page api

base_url = "https://api.instatus.com/v1"
token="f415879e72559617ea8e536f1f710d38"
page_id = "clv53955s6985b9ojsm90awpb"
component_id = ["clw67x7cd7000bilj0n7xh851", "clwsx9hko495721q5n49bc8lyly"]
url = f"{base_url}/{page_id}/components?page=:page&per_page=:per_page" # api to fetch all components from status page
# url = f"{base_url}/{page_id}/components/{component_id}" # api to fetch specific component

headers = {
    "Authorization": f"Bearer {token}"
}

# without loop

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=4))
else:
    print(f"Failed to fetch data for ID {id} {response.status_code}")

# with loop

# for id in component_id:
#     url = f"{base_url}/{page_id}/components/{id}"
#     print(url)
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         data = response.json()
#         print(json.dumps(data, indent=4))
#     else:
#         print(f"Failed to fetch data for ID {id} {response.status_code}")