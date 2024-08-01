import json
from api_call.arium.util.currency_table import Currency, CurrencyTable
from api_call.arium.util.analysis_request import (
    AnalysisRequest,
    AnalysisAsset,
)
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set assets' ref id
portfolio_id = "example-portfolio-reference"
reinsurance_id = "example-reinsurance-reference"
currency_id = "example-currency-reference"
# Create request
request_object = AnalysisRequest()

# Option 1: Use existing saved event set without modification
# REQUIRED ACTION: Set saved event set ref id
asset_id = "example-asset-reference"

# Option 2: Use existing analysis asset and modify
# REQUIRED ACTION: Set saved event set ref id
asset_object = AnalysisAsset(
    **json.loads(client.analysis().get_data(asset_id=asset_id))
)
asset_object.set_number_of_runs(10000)
asset_object.set_random_seed(1)
asset_object.set_minimum_groundup(10000)
asset = client.analysis().create("test ceded loss", data=asset_object.get())
new_asset_id = asset["id"]

# Set other request parameters
# Add export type "custom" for cededLossesPerTreaty
request_object.add_csv_export(export_type="custom", custom_id="CededLossesPerTreaty")

# Assign analysis asset to request (use asset_id from option 1 or new_asset_id from option 2)
request_object.set_analysis_reference(new_asset_id, portfolio=portfolio_id)
# Assign reinsurance asset to request
request_object.set_reinsurance_reference(reinsurance_id)
request_object.set_currency_reference(currency_id)
# Run calculations
result = client.calculations().analysis(
    request=request_object.get(), name="test_ceded_loss"
)

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
