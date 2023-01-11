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

# Update portfolio description
client.portfolios().set_description(portfolio_id, "new portfolio description")

updated_description = client.portfolios().get_description(portfolio_id)
print(f"portfolio description: {updated_description}")
