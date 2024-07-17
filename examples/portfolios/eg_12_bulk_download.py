import os

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set output folder path
output_folder = "data_download/"
portfolios = {p["name"]: p["id"] for p in client.portfolios().list()}

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

succeeded = []
failed = []

for portfolio_name, portfolio_id in portfolios.items():
    try:
        portfolio_data = client.portfolios().get_data(portfolio_id)

        with open(
            output_folder + portfolio_name + ".csv", "w", encoding="utf-8", newline=""
        ) as f:
            print(f"Saving {portfolio_name} ({portfolio_id})...")
            f.write(portfolio_data.decode("utf-8"))
        succeeded.append(portfolio_name)
    except Exception as e:
        failed.append(portfolio_name)
        print(
            f"Failed to download portfolio {portfolio_name} ({portfolio_id}). Reason: '{e}'. Skipping."
        )

print("Finished bulk download.")
print(f"Succeeded: {succeeded}")
print(f"Failed: {failed}")
