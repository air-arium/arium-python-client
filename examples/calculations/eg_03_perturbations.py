from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Update request
# Run calculations
result = client.calculations().perturbations(request="./data/perturbations.json")

# Display
for export in result:
    for row in export:
        print(row)
