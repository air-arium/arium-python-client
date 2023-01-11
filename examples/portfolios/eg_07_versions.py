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

# Get version of portfolio
portfolio_versions_list = client.portfolios().versions(portfolio_id)
print(f"versions: {len(portfolio_versions_list)}")
for portfolio in portfolio_versions_list:
    print(f"portfolio: {json.dumps(portfolio, sort_keys=True, indent=4)}")
