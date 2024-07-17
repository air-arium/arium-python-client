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

# Update event description
client.events().set_description(event_id, "new description")

# Get event description
updated_description = client.events().get_description(event_id)
print(f"event description: {updated_description}")

# Update event specific file description
client.events().set_payload_description(event_id, "new payload description")

# Get event specific file description
updated_payload_description = client.events().get_payload_description(event_id)
print(f"event payload description: {updated_payload_description}")
