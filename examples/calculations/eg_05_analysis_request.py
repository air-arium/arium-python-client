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

# Select ids
# REQUIRED ACTION: Set ref ids of the assets
portfolio_id = "example-portfolio-reference"
event_id = "example-event-reference"
size_data_id = "example-size-reference"
currency_id = "example-currency-reference"

# Create analysis asset
asset_object = AnalysisAsset()

# Create groups. Optionally set frequency parameters
# Add one or more events to each group. Use group index to assign events to groups
group_1 = asset_object.create_group(group_name="Group 1", events=[event_id])
group_2 = asset_object.create_group(
    group_name="Group 2", frequency=0.1, events=[event_id]
)

# Set number of runs and random seed
asset_object.set_number_of_runs(100)
asset_object.set_random_seed(1)

# Upload
asset = client.analysis().create("test LA", data=asset_object.get())


# Create request
request_object = AnalysisRequest()

# Set currency
request_object.set_currency_reference(currency_id)

# Alternatively set currency by value
# currency_eur = Currency(code="EUR", rate=1.0)
# currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
# request_object.set_currency(currency_table)

# Define export parameters
request_object.add_csv_export(
    export_type="simulation",
    characteristics=["RunId", "ScenarioId"],
    metrics=["GrossLoss"],
)

# Optionally set size data
# request_object.set_size_data(size_data_id)

# Add LA reference to request and define portfolio
request_object.set_analysis_reference(reference=asset["id"], portfolio=portfolio_id)

# Convert request and asset.json to dictionary
request_dict = request_object.get()

# Run calculations
result = client.calculations().analysis(request=request_dict)

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
