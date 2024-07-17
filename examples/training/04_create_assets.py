import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Define okta auth parameters
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)
print(client)

# REQUIRED ACTION: Set path to event file
# Create event
print("CREATE EVENT")
with open("path/to/event.json") as file:
    data = json.load(file)
new_event = client.events().create("test-event-2", data)
print(f"event: {json.dumps(new_event, sort_keys=True, indent=4)}")

# REQUIRED ACTION: Set path to portfolio file
# Create portfolio
print("CREATE PORTFOLIO")
with open("path/to/portfolio.csv") as file:
    data = file.read()
portfolio = client.portfolios().create(f"test-portfolio-2", data)
print(f"portfolio: {json.dumps(portfolio, sort_keys=True, indent=4)}")
