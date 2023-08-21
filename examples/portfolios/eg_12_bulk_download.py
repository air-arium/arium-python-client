import os

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

output_folder = "data_download/"
portfolios = {p["name"]: p["id"] for p in client.portfolios().list()}

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for portfolio_name, portfolio_id in portfolios.items():
    portfolio_data = client.portfolios().get_data(portfolio_id)

    with open(output_folder + portfolio_name + ".csv", "w", encoding="utf-8") as f:
        print(f"Saving {portfolio_name} ({portfolio_id})...")
        f.write(portfolio_data.decode("utf-8"))

print("Finished bulk download.")
