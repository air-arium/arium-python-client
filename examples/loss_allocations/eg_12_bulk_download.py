import os

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

output_folder = "data_download/"
loss_allocations = {p["name"]: p["id"] for p in client.loss_allocations().list()}

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for loss_allocation_name, loss_allocation_id in loss_allocations.items():
    loss_allocation_data = client.loss_allocations().get_data(loss_allocation_id)

    with open(
        output_folder + loss_allocation_name + ".json", "w", encoding="utf-8"
    ) as f:
        print(f"Saving {loss_allocation_name} ({loss_allocation_id})...")
        f.write(loss_allocation_data.decode("utf-8"))

print("Finished bulk download.")
