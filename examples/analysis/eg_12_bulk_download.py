import os

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set path to folder where downloaded assets should be stored
output_folder = "data_download/"
analysis = {p["name"]: p["id"] for p in client.analysis().list()}

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for analysis_name, analysis_id in analysis.items():
    analysis_data = client.analysis().get_data(analysis_id)

    with open(output_folder + analysis_name + ".json", "w", encoding="utf-8") as f:
        print(f"Saving {analysis_name} ({analysis_id})...")
        f.write(analysis_data.decode("utf-8"))

print("Finished bulk download.")
