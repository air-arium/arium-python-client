from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new Auth
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)

# Create new client
client = APIClient(auth=auth)

# Display client data
print(client)

# Access dedicated clients
calculations_client = client.calculations()
portfolios_client = client.portfolios()
scenarios_client = client.scenarios()
