import json
import os
from time import sleep

from api_call.client import APIClient
from auth.okta_auth import Auth

prefix = ""
settings = {}

# Create new client
auth = Auth(
    tenant="workspace1",
    role="basic",
    settings=settings,
    prefix=prefix,
    verify=False,
)
client = APIClient(auth=auth)

# Import all scenarios from input folder
input_folder = "data/"
override = True
scenarios = {p["name"]: p["id"] for p in client.scenarios().list()}
uploading = []


for subdir, dirs, files in os.walk(input_folder):
    for file in files:
        filepath = os.path.join(subdir, file).replace("\\", "/")
        name = filepath.replace(input_folder, "").replace(".json", "")
        if override or name not in scenarios.keys():
            print(f"Create {name}...")
            with open(filepath) as f:
                data = json.load(f)
            asset = client.scenarios().create(name, data=data)
            uploading.append(asset["id"])


while uploading:
    sleep(5)
    scenarios_ids = uploading.copy()
    for scenario_id in scenarios_ids:
        scenario = client.portfolios().get(scenario_id)
        if scenario["status"] in ("uploading", "processing"):
            continue
        elif scenario["status"] == "error":
            print(f"Error uploading scenario {scenario['name']} ({scenario['id']}).")
            uploading.remove(scenario_id)
        else:
            print(f"Uploaded {scenario['name']} ({scenario['id']}).")
            uploading.remove(scenario_id)

print("Finished bulk upload.")
