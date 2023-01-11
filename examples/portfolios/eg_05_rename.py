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

# Rename portfolio
portfolio = client.portfolios().rename(portfolio_id, "renamed_portfolio")
print(f"portfolio: {json.dumps(portfolio, sort_keys=True, indent=4)}")
