import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set path to portfolio
# Create portfolio
with open("path/to/portfolio.csv") as file:
    data = file.read()
portfolio = client.portfolios().create(f"portfolio-test", data)
print(f"portfolio: {json.dumps(portfolio, sort_keys=True, indent=4)}")
