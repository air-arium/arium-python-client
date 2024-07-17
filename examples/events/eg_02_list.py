import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# Get list of latest versions of events assets
latest_events_list = client.events().list()
for event in latest_events_list:
    print(f"event (latest): {json.dumps(event, sort_keys=True, indent=4)}")

# Get list of all versions of events assets
all_events_list = client.events().list(latest=False)
for event in all_events_list:
    print(f"event: {json.dumps(event, sort_keys=True, indent=4)}")
