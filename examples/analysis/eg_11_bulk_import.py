import json
import os
from time import sleep

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set path to folder with data
# Import all analysis from input folder
input_folder = "data/"
override = True
analysis = {p["name"]: p["id"] for p in client.analysis().list()}
uploading = []

for file in os.listdir(input_folder):
    name = file.replace(".json", "")
    if override or name not in analysis.keys():
        print(f"Create {name}...")
        with open(input_folder + file) as f:
            data = json.load(f)
        asset = client.analysis().create(name, data=data, wait=False)
        uploading.append(asset["id"])

while uploading:
    sleep(5)
    analysis_ids = uploading.copy()
    for analysis_id in analysis_ids:
        analysis_asset = client.analysis().get(analysis_id)
        if analysis_asset["status"] in ("uploading", "processing"):
            continue
        elif analysis_asset["status"] == "error":
            print(
                f"Error uploading analysis {analysis_asset['name']} ({analysis_asset['id']})."
            )
            uploading.remove(analysis_id)
        else:
            print(f"Uploaded {analysis_asset['name']} ({analysis_asset['id']}).")
            uploading.remove(analysis_id)

print("Finished bulk upload.")
