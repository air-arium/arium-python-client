from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# Run calculations
# REQUIRED ACTION: Set path to a json file with request data
result = client.calculations().analysis(request="./path/to/sizes.json")

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
