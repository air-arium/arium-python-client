import json

from api_call.client import APIClient
from auth.okta_auth import Auth
from config.constants import CLIENT_ID, CLIENT_SECRET, AUTH_SERVER, ISSUER, AUDIENCE

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)


with open("./data/request.json") as f:
    request = json.load(f)

for group in request["lossAllocation"]["groups"]:
    print(
        f"{group['title']} settings: "
        f"frequencyMode='{group.get('frequencyMode')}', "
        f"equalWeighted='{group.get('equalWeighted')}'"
    )
    # You can change frequency settings
    # group["frequencyMode"] = ...
    # group["equalWeighted"] = ...

# Run calculations
result = client.calculations().loss_allocation(request=request)

# Display
for export in result:
    for row in export:
        print(row)
