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

# Get versions of scenario
scenario_versions_list = client.scenarios().versions(scenario_id)
print(f"versions: {len(scenario_versions_list)}")
for scenario in scenario_versions_list:
    print(f"scenario version: {json.dumps(scenario, sort_keys=True, indent=4)}")
