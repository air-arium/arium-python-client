import json
import os
from time import sleep

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(
    tenant="workspace1",
    role="basic",
    settings=auth_settings,
    prefix=prefix,
)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set input folder path
# Import all events from input folder
input_folder = "data/"
override = True
events = {p["name"]: p["id"] for p in client.events().list()}
uploading = []


for subdir, dirs, files in os.walk(input_folder):
    for file in files:
        filepath = os.path.join(subdir, file).replace("\\", "/")
        name = filepath.replace(input_folder, "").replace(".json", "")
        if override or name not in events.keys():
            print(f"Create {name}...")
            with open(filepath) as f:
                data = json.load(f)
            asset = client.events().create(name, data=data)
            uploading.append(asset["id"])


while uploading:
    sleep(5)
    events_ids = uploading.copy()
    for event_id in events_ids:
        event = client.portfolios().get(event_id)
        if event["status"] in ("uploading", "processing"):
            continue
        elif event["status"] == "error":
            print(f"Error uploading event {event['name']} ({event['id']}).")
            uploading.remove(event_id)
        else:
            print(f"Uploaded {event['name']} ({event['id']}).")
            uploading.remove(event_id)

print("Finished bulk upload.")
