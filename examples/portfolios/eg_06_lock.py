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
