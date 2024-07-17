from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set path to credentials file
prefix = ""
file = ""

# Create new Auth
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
auth = Auth(tenant="workspace1", role="basic", settings=file, prefix=prefix)

# Create client
client = APIClient(auth=auth)
print(client)
