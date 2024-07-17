from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set path to file with sizes
# Create sizes:
with open("path/to/sizes.csv") as file:
    data = file.read()

new_sizes = client.sizes().create(f"test-sizes", data)
print(new_sizes)
