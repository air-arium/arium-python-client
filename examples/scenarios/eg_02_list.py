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

# Get list of latest versions of scenarios assets
latest_scenarios_list = client.scenarios().list()
for scenario in latest_scenarios_list:
    print(f"scenario (latest): {json.dumps(scenario, sort_keys=True, indent=4)}")

# Get list of all versions of scenarios assets
all_scenarios_list = client.scenarios().list(latest=False)
for scenario in all_scenarios_list:
    print(f"scenario: {json.dumps(scenario, sort_keys=True, indent=4)}")
