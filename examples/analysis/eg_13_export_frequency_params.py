from api_call.client import APIClient
from auth.okta_auth import Auth
import json

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)
# REQUIRED ACTION: Set reference ID
response = client.refdata().get("frequency-params")

print(json.dumps(response, indent=4))
print("Finished frequency parameters export.")
