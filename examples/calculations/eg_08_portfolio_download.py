import json

from api_call.client import APIClient
from auth.okta_auth import Auth


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

rows = client.calculations().portfolio_download(request="./data/request.json")
for row in rows:
    print(row)
