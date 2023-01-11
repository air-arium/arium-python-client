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

# REQUIRED ACTION: Select portfolio id
portfolio_id = ""

# Get individual portfolio content
portfolio_full = client.portfolios().get(portfolio_id)
print(f"portfolio: {json.dumps(portfolio_full, sort_keys=True, indent=4)}")

# Get list of latest versions of portfolios assets
latest_portfolios_list = client.portfolios().list()

for portfolio in latest_portfolios_list:
    # Get individual portfolio content
    portfolio_full = client.portfolios().get(portfolio["id"])
    print(f"portfolio: {json.dumps(portfolio_full, sort_keys=True, indent=4)}")
