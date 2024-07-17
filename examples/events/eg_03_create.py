import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set path to a json file with event data
# Create event
with open("path/to/event.json") as file:
    data = json.load(file)
    new_event = client.events().create("test-event-1", data)
    print(f"event: {json.dumps(new_event, sort_keys=True, indent=4)}")
