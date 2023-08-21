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

# Import all loss_allocations from input folder
input_folder = "data/"
override = True
loss_allocations = {p["name"]: p["id"] for p in client.loss_allocations().list()}
uploading = []

for file in os.listdir(input_folder):
    name = file.replace(".json", "")
    if override or name not in loss_allocations.keys():
        print(f"Create {name}...")
        with open(input_folder + file) as f:
            data = json.load(f)
        asset = client.loss_allocations().create(name, data=data, wait=False)
        uploading.append(asset["id"])

while uploading:
    sleep(5)
    loss_allocations_ids = uploading.copy()
    for loss_allocation_id in loss_allocations_ids:
        loss_allocation = client.loss_allocations().get(loss_allocation_id)
        if loss_allocation["status"] in ("uploading", "processing"):
            continue
        elif loss_allocation["status"] == "error":
            print(
                f"Error uploading loss_allocation {loss_allocation['name']} ({loss_allocation['id']})."
            )
            uploading.remove(loss_allocation_id)
        else:
            print(f"Uploaded {loss_allocation['name']} ({loss_allocation['id']}).")
            uploading.remove(loss_allocation_id)

print("Finished bulk upload.")
