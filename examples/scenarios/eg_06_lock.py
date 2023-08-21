from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Select scenario id
scenario_id = ""

# Check if scenario is locked
is_locked = client.scenarios().is_locked(scenario_id)
print(f"scenario is_locked: {is_locked}")

# Lock scenario
client.scenarios().lock(scenario_id)
is_locked = client.scenarios().is_locked(scenario_id)
print(f"scenario is_locked: {is_locked}")

# Unlock scenario
client.scenarios().unlock(scenario_id)
is_locked = client.scenarios().is_locked(scenario_id)
print(f"scenario is_locked: {is_locked}")
