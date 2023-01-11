from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
file = ""

# Create new Auth
auth = Auth(tenant="workspace1", role="basic", connections=file, prefix=prefix)

# Create client
client = APIClient(auth=auth)
print(client)
