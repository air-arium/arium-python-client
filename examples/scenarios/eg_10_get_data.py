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

scenario_data = client.scenarios().get_data(scenario_id)
scenario_json = json.loads(scenario_data)

print(f"scenario payload data: {json.dumps(scenario_json, sort_keys=True, indent=4)}")
