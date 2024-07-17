import os
from datetime import datetime
from time import sleep

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set input folder path
# Import all portfolios from input folder
input_folder = "data"
override = True
portfolios = {p["name"]: p["id"] for p in client.portfolios().list()}
uploading = []
start_time = {}

for file in os.listdir(input_folder):
    name = input_folder + "___" + file.replace(".csv", "")
    print(f"Create {name}...")
    asset = client.portfolios().create(name, file=input_folder + "/" + file, wait=False)
    uploading.append(asset["id"])
    start_time[asset["id"]] = datetime.now()

while uploading:
    sleep(5)
    portfolios_ids = uploading.copy()
    for portfolio_id in portfolios_ids:
        portfolio = client.portfolios().get(portfolio_id)
        if portfolio["status"] in ("uploading", "processing"):
            continue
        elif portfolio["status"] == "error":
            print(
                f"Error uploading portfolio {portfolio['name']} ({portfolio['id']}). "
                f"Time {(datetime.now() - start_time[portfolio['id']]) / 60} "
            )
            uploading.remove(portfolio_id)
            print(f"Log:\n" f"{portfolio['errors']}")
        else:
            print(
                f"Uploaded {portfolio['name']} ({portfolio['id']})."
                f"Time {(datetime.now() - start_time[portfolio['id']]) / 60}"
            )
            uploading.remove(portfolio_id)

print("Finished bulk upload.")
