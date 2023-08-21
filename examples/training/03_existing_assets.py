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
print(client)

# REQUIRED ACTION: Select scenario id
scenario_id = ""

# Get individual scenario content
print("GET")
scenario_full = client.scenarios().get(scenario_id)
print(f"scenario: {json.dumps(scenario_full, sort_keys=True, indent=4)}")

# Get versions
print("VERSIONS")
versions = client.scenarios().versions(scenario_id)

for scenario in versions:
    # Get individual scenario content
    scenario_full = client.scenarios().get(scenario["id"])
    print(f"scenario: {json.dumps(scenario_full, sort_keys=True, indent=4)}")

# Get list of latest versions of scenarios assets
print("LIST")
scenarios_list = client.scenarios().list()

for scenario in scenarios_list:
    # Get individual scenario content
    scenario_full = client.scenarios().get(scenario["id"])
    print(f"scenario: {json.dumps(scenario_full, sort_keys=True, indent=4)}")

# It is the same for each asset
print("LIST (PORTFOLIOS)")
portfolios_list = client.portfolios().list()
print(f"portfolios: {json.dumps(portfolios_list, sort_keys=True, indent=4)}")

# Non existing scenario case
print("ERROR")
scenario_full = client.scenarios().get("not_a_valid_reference")
