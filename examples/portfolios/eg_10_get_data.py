import io

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

portfolio_data = client.portfolios().get_data(portfolio_id)

print(f"portfolio payload data: \n")
for line in io.StringIO(portfolio_data.decode('utf-8')):
    print(repr(line))
