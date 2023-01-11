from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
client = APIClient(auth=auth)

# Create sizes:
with open('./data/sizes.csv') as file:
    data = file.read()

new_sizes = client.sizes().create(f"test-sizes", data)
print(new_sizes)
