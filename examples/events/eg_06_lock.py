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

# Check if event is locked
is_locked = client.events().is_locked(event_id)
print(f"event is_locked: {is_locked}")

# Lock event
client.events().lock(event_id)
is_locked = client.events().is_locked(event_id)
print(f"event is_locked: {is_locked}")

# Unlock event
client.events().unlock(event_id)
is_locked = client.events().is_locked(event_id)
print(f"event is_locked: {is_locked}")
