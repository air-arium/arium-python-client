from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Select scenario id
scenario_id = ""

# Update scenario description
client.scenarios().set_description(scenario_id, "new description")

# Get scenario description
updated_description = client.scenarios().get_description(scenario_id)
print(f"scenario description: {updated_description}")

# Update scenario specific file description
client.scenarios().set_payload_description(scenario_id, "new payload description")

# Get scenario specific file description
updated_payload_description = client.scenarios().get_payload_description(scenario_id)
print(f"scenario payload description: {updated_payload_description}")
