from api_call.arium.util.currency_table import CurrencyTable, Currency
from api_call.arium.util.loss_allocation_request import LossAllocationRequest
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)
print(client)

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
    "numberOfRuns": 1000,
    "randomSeed": 1,
    "lossAllocation": {
        "groups": [
            {
                "scenarios": [
                    {
                        "title": "Test scenario",
                        "ref": "210dddfe-a913-5e47-bf56-de72d0d7b28a",  # "LA"
                        "portfolio": {
                            "ref": "3c70494b-a7d5-5ce2-a620-ce4fcde78b9f"
                        },  # 362
                    },
                ],
                "title": "group1",
                "settings": {},
            }
        ]
    },
    "currency": [{"code": "usd", "rate": 1}],
}

# Define request as an object
request_object = LossAllocationRequest()
request_object.set_currency(
    value=CurrencyTable(name="My currency", currencies=[Currency(code="usd", rate=1)])
)
request_object.set_loss_allocation_reference(
    reference="7a64c98b-81f8-5d84-ac20-600e6071026c",
    portfolio="3c70494b-a7d5-5ce2-a620-ce4fcde78b9f",
)
request_object.set_number_of_runs(1000)
request_object.set_random_seed(1)
request_object.add_csv_export(
    characteristics=["ScenarioId", "PolicyNumber"],
    metrics=["InsuredLoss"],
    export_type="simulation",
)

# Run calculations (using dictionary, file, object)
result_1 = list(client.calculations().loss_allocation(request=request))
result_2 = list(
    client.calculations().loss_allocation(request="./data/training_request.json")
)
result_3 = list(client.calculations().loss_allocation(request=request_object.get()))

for export in result_3:
    for row in export:
        print(row)
