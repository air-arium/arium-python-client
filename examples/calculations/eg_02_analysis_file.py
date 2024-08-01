from api_call.client import APIClient
from auth.okta_auth import Auth

# Please note that using JSON request only without specifying custom analysis settings
# will run the calculations using parameters specified in referenced saved event set asset

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="test", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# Run calculations
# REQUIRED ACTION: Set path to a json file with request data
result = client.calculations().analysis(request="path/to/request.json")

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
