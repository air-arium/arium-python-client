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

# Create portfolio
with open('./data/3.csv') as file:
    data = file.read()
portfolio = client.portfolios().create(f"362", data)
print(f"portfolio: {json.dumps(portfolio, sort_keys=True, indent=4)}")
