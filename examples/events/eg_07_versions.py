import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set ref ids
# Select event id
event_id = "example-event-reference"

# Get versions of event
event_versions_list = client.events().versions(event_id)
print(f"versions: {len(event_versions_list)}")
for event in event_versions_list:
    print(f"event version: {json.dumps(event, sort_keys=True, indent=4)}")
