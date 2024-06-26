import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)

# Create scenario
with open("./data/scenario.json") as file:
    data = json.load(file)
    new_scenario = client.scenarios().create("test-scenario-1", data)
    print(f"scenario: {json.dumps(new_scenario, sort_keys=True, indent=4)}")
