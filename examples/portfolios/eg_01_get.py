import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set ref ids
# Select portfolio id
portfolio_id = "example-portfolio-reference"

# Get individual portfolio content
portfolio_full = client.portfolios().get(portfolio_id)
print(f"portfolio: {json.dumps(portfolio_full, sort_keys=True, indent=4)}")

# Get list of latest versions of portfolios assets
latest_portfolios_list = client.portfolios().list()

for portfolio in latest_portfolios_list:
    # Get individual portfolio content
    portfolio_full = client.portfolios().get(portfolio["id"])
    print(f"portfolio: {json.dumps(portfolio_full, sort_keys=True, indent=4)}")
