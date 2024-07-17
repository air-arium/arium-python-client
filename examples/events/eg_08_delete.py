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

# Delete event
client.events().delete(event_id)

event = client.events().get(event_id)
print(f"event status: {event['status']}")
