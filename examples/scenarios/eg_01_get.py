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

# Get individual scenario content
scenario_full = client.scenarios().get(scenario_id)
print(f"scenario: {json.dumps(scenario_full, sort_keys=True, indent=4)}")

# Get list of latest versions of scenarios assets
latest_scenarios_list = client.scenarios().list()

for scenario in latest_scenarios_list:
    # Get individual scenario content
    scenario_full = client.scenarios().get(scenario["id"])
    print(f"scenario: {json.dumps(scenario_full, sort_keys=True, indent=4)}")
