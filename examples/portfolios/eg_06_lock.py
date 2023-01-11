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

# Check if portfolio is locked
is_locked = client.portfolios().is_locked(portfolio_id)
print(f"portfolio is_locked: {is_locked}")

# Lock portfolio
client.portfolios().lock(portfolio_id)
is_locked = client.portfolios().is_locked(portfolio_id)
print(f"portfolio is_locked: {is_locked}")

# Unlock portfolio
client.portfolios().unlock(portfolio_id)
is_locked = client.portfolios().is_locked(portfolio_id)
print(f"portfolio is_locked: {is_locked}")
