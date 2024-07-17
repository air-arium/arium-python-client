from api_call.arium.util.analysis_request import AnalysisRequest

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set ref ids

# Select saved event set id
a_id = "example-asset-reference"

# Select portfolio id
portfolio_id = "example-portfolio-reference"

# Select currency table id
currency_table_id = "example-currency-reference"

# Create request
request_object = AnalysisRequest()
request_object.set_analysis_reference(reference=a_id, portfolio=portfolio_id)
request_object.set_currency_reference(currency_table_id)

request_object.add_csv_export(
    export_type="simulation",
    characteristics=["ScenarioId"],
    metrics=[
        "EconomicLoss",
        "DefenceCost",
        "NonEconomicLoss",
        "PolicyNumber",
        "GrossLoss",
    ],
    export_non_zero_gross_loss=False,
)

# Run calculations
result = client.calculations().analysis(request=request_object.get())

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
