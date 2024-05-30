import requests
import json

base_url="https://api.instatus.com/v1"
page_id = "clv53955s6985b9ojsm90awpb"
url = f"{base_url}/{page_id}/components"
token="f415879e72559617ea8e536f1f710d38"

json_data_list = [{
  "name": "https://auth.wiser.com",
  "description": "Components created through looping",
  "status": "OPERATIONAL",
  "order": 6,
  "showUptime": True,
  "grouped": False,
  "archived": False  
},
{
  "name": "https://channelsync.com",
  "description": "Components created through looping",
  "status": "OPERATIONAL",
  "order": 6,
  "showUptime": True,
  "grouped": False,
  "archived": False  
}]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

for json_data in json_data_list:
    
    response = requests.post(url, headers=headers, json=json_data)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=4))
else:
    print("Failed to post data:", response.status_code)
    print(f"Response content: {response.content.decode()}")