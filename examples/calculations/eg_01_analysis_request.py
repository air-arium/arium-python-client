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
auth = Auth(tenant="test", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set portfolio ref id and select one the options below
# Select portfolio id
portfolio_id = "example-portfolio-reference"

# Create request
request_object = AnalysisRequest()

# Option 1: Use existing saved event set without modification
# REQUIRED ACTION: Set saved event set ref id
a_id_1 = "example-asset-reference"

# Option 2: Create new saved event set (settings)
# REQUIRED ACTION: Set asset object parameters
asset_object = AnalysisAsset()
asset_object.set_number_of_runs(1000)
asset_object.set_random_seed(1)
asset_object.set_minimum_groundup(10005)
asset_object.create_group("Test events group", events=["example-event-reference"])
asset = client.analysis().create("test LA", data=asset_object.get())
a_id_2 = asset["id"]

# Option 3: Use existing saved event set and modify
# REQUIRED ACTION: Set saved event set ref id
asset_object = AnalysisAsset(**json.loads(client.analysis().get_data(asset_id=a_id_2)))
asset_object.set_number_of_runs(1000)
asset_object.set_random_seed(1)
asset_object.set_minimum_groundup(10000)
asset = client.analysis().create("test LA", data=asset_object.get())
a_id_3 = asset["id"]


assert a_id_1 != a_id_2 != a_id_3

# Set other request parameters
currency_eur = Currency(code="EUR", rate=1.0)
currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
request_object.set_currency(currency_table)
request_object.add_csv_export(
    export_type="simulation", characteristics=["ScenarioId"], metrics=["GrossLoss"]
)

# Assign analysis asset to request (use LA id from option 1 or 2 or 3)
request_object.set_analysis_reference(a_id_3, portfolio=portfolio_id)

# Run calculations
result = client.calculations().analysis(request=request_object.get(), name="test_LA")

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
