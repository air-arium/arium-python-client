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
print(client)

# Create scenario
print("CREATE SCENARIO")
with open('./data/scenario.json') as file:
    data = json.load(file)
new_scenario = client.scenarios().create("test-scenario-2", data)
print(f"scenario: {json.dumps(new_scenario, sort_keys=True, indent=4)}")

# Create portfolio
print("CREATE PORTFOLIO")
with open('./data/1322_custom.csv') as file:
    data = file.read()
portfolio = client.portfolios().create(f"test-1322-custom", data)
print(f"portfolio: {json.dumps(portfolio, sort_keys=True, indent=4)}")
