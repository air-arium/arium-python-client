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

# Delete scenario
client.scenarios().delete(scenario_id)

scenario = client.scenarios().get(scenario_id)
print(f"scenario status: {scenario['status']}")
