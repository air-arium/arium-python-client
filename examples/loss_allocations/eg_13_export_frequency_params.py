from api_call.client import APIClient
from auth.okta_auth import Auth
import json

prefix = ""
settings = {}

# Create new client
auth = Auth(
    tenant="workspace1",
    role="basic",
    settings=settings,
    prefix=prefix,
    verify=False,
)
client = APIClient(auth=auth)

response = client.refdata().get('frequency-params')

print(json.dumps(response, indent=4))
print("Finished frequency parameters export.")
