from api_call.arium.util.currency_table import Currency, CurrencyTable
from api_call.arium.util.analysis_request import AnalysisRequest
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace2", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set ref ids

# Select saved event set id
a_id = "example-asset-reference"

# Select portfolio id
portfolio_id = "example-portfolio-reference"

# Create request
request_object = AnalysisRequest()
request_object.set_analysis_reference(reference=a_id, portfolio=portfolio_id)
currency_eur = Currency(code="EUR", rate=1.0)
currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
request_object.set_currency(currency_table)
request_object.add_csv_export(
    export_type="simulation",
    characteristics=["ScenarioId"],
    metrics=["GrossLoss"],
    export_non_zero_gross_loss=False,
)
# Run calculations
result = client.calculations().analysis(
    request=request_object.get(), name="test_A_clean_up_3"
)
# Check status
print(result)
# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)
