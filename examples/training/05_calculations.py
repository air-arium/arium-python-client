from api_call.arium.util.currency_table import CurrencyTable, Currency
from api_call.arium.util.analysis_request import (
    AnalysisRequest,
    AnalysisAsset,
)
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

# REQUIRED ACTION: Set request parameters
# Define request as a dictionary
request = {
    "export": {
        "csv": [
            {
                "type": "simulation",
                "characteristics": ["ScenarioId", "PolicyNumber"],
                "metrics": ["InsuredLoss"],
            }
        ]
    },
    "lossAllocation": {
        "ref": "example-asset-reference",
        "portfolio": {"ref": "example-portfolio-reference"},
    },
    "currency": [{"code": "usd", "rate": 1}],
}

# REQUIRED ACTION: Set asset object and/or request object parameters
# Define request as an object
request_object = AnalysisRequest()
asset_object = AnalysisAsset()
request_object.set_currency(
    value=CurrencyTable(name="My currency", currencies=[Currency(code="usd", rate=1)])
)
request_object.set_analysis_reference(
    reference="example-asset-reference",
    portfolio="example-portfolio-reference",
)
asset_object.set_number_of_runs(1000)
asset_object.set_random_seed(1)
request_object.add_csv_export(
    characteristics=["ScenarioId", "PolicyNumber"],
    metrics=["InsuredLoss"],
    export_type="simulation",
)

# REQUIRED ACTION: select which method of getting analysis results should be used
# Run calculations (using: 1: dictionary, 2: file, 3: object)
# method 1
result_1 = list(client.calculations().analysis(request=request))
# REQUIRED ACTION: Set path to a json file with request data
# method 2
result_2 = list(client.calculations().analysis(request="path/to/request.json"))
# method 3
result_3 = list(client.calculations().analysis(request=request_object.get()))

# REQUIRED ACTION: Set the reference to the selected result

for row in result_1:
    print(row)
