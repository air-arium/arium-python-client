import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# Select event id
event_id = "example-event-reference"

# Rename event
event = client.events().rename(event_id, f"renamed-event")
print(f"event: {json.dumps(event, sort_keys=True, indent=4)}")
