from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Select portfolio id
portfolio_id = ""

# Delete portfolio
client.portfolios().delete(portfolio_id)

deleted_portfolio = client.portfolios().get(portfolio_id)
print(f"portfolio status: {deleted_portfolio['status']}")
