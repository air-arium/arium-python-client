import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set event ref id
# Select event id
event_id = "example-event-reference"

# Get individual event content
event_full = client.events().get(event_id)
print(f"event: {json.dumps(event_full, sort_keys=True, indent=4)}")

# Get list of latest versions of events assets
latest_events_list = client.events().list()

for event in latest_events_list:
    # Get individual event content
    event_full = client.events().get(event["id"])
    print(f"event: {json.dumps(event_full, sort_keys=True, indent=4)}")
