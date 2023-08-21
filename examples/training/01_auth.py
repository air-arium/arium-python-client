from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new Auth
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
print(auth)
