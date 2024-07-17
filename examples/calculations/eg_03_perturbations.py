from api_call.client import APIClient
from auth.okta_auth import Auth
from api_call.arium.util.currency_table import Currency, CurrencyTable
from api_call.arium.util.analysis_request import (
    AnalysisRequest,
    AnalysisAsset,
)

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)


# Create request and asset, then run calculations

# portfolio id
# REQUIRED ACTION: Set portfolio ref id
portfolio_id = "example-portfolio-reference"

# Create request
request_object = AnalysisRequest()

# Create new analysis asset (settings)
# REQUIRED ACTION: Set asset object parameters
asset_object = AnalysisAsset()
asset_object.set_number_of_runs(1000)
asset_object.set_random_seed(1)
asset_object.set_minimum_groundup(10005)
asset_object.create_group(
    "Test events group perturbations", events=["example-event-reference"]
)
# set asset perturbations to True
asset_object.set_perturbations(True)
asset = client.analysis().create("test asset perturbations", data=asset_object.get())

currency_eur = Currency(code="EUR", rate=1.0)
currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
request_object.set_currency(currency_table)

request_object.add_csv_export(
    export_type="simulation", characteristics=["ScenarioId"], metrics=["GrossLoss"]
)

request_object.set_analysis_reference(asset["id"], portfolio=portfolio_id)

# Run calculations
result = client.calculations().analysis(
    request=request_object.get(), name="test_perturbations"
)

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
