import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Select scenario id
scenario_id = ""

# Rename scenario
scenario = client.scenarios().rename(scenario_id, f"renamed-scenario")
print(f"scenario: {json.dumps(scenario, sort_keys=True, indent=4)}")
