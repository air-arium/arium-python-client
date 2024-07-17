import os

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set output folder path
output_folder = "data_download/"
events = {p["name"]: p["id"] for p in client.events().list()}

for event_name, event_id in events.items():
    event_data = client.events().get_data(event_id)
    try:
        filepath = output_folder + event_name
        filepath = filepath.strip()
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath + ".json", "w", encoding="utf-8") as f:
            print(f"Saving {event_name} ({event_id})...")
            f.write(event_data.decode("utf-8"))
    except Exception as e:
        print()

print("Finished bulk download.")
