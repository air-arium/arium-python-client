from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new Auth
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
print(auth)
