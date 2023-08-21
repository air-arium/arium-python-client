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
scenarios = {p["name"]: p["id"] for p in client.scenarios().list()}

for scenario_name, scenario_id in scenarios.items():
    scenario_data = client.scenarios().get_data(scenario_id)
    try:
        filepath = output_folder + scenario_name
        filepath = filepath.strip()
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath + ".json", "w", encoding="utf-8") as f:
            print(f"Saving {scenario_name} ({scenario_id})...")
            f.write(scenario_data.decode("utf-8"))
    except Exception as e:
        print()

print("Finished bulk download.")
