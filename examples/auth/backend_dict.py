from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = ""
auth_settings = {}

# Create new Auth
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)

# Create client
client = APIClient(auth=auth)
print(client)
