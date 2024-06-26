from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)

# Create sizes:
with open("./data/sizes.csv") as file:
    data = file.read()

new_sizes = client.sizes().create(f"test-sizes", data)
print(new_sizes)
