import json
import requests

base_url="https://api.instatus.com/v1"
page_id = "clv53955s6985b9ojsm90awpb"
token="f415879e72559617ea8e536f1f710d38"
components_id = ["clwt8qcjr1009563pyn4uh5iy9lg", "clwt8qbkg1475900wdn68573dod8", "clwt7owb2959071pyn4fg71p4qb",
                 "clwt7nkef1411341vzn6q4ww7tex", "clwsx9hko495721q5n49bc8lyly", "clwqk9yl146512krodf59x4hwm"]
headers = {
    "Authorization": f"Bearer {token}"
}

for id in components_id:
    url = f"{base_url}/{page_id}/components/{id}"
    print(url)
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=4))
    else:
        print(f"Failed to fetch data for ID {id} {response.status_code}")    