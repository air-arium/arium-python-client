from api_call.arium.util.currency_table import CurrencyTable, Currency
from api_call.arium.util.loss_allocation_request import LossAllocationRequest
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
client = APIClient(auth=auth)
print(client)

# REQUIRED ACTION: Define request as a dictionary (update references)
request = {
    "export": {
        "csv": [
            {
                "type": "simulation",
                "characteristics": [
                    "ScenarioId",
                    "PolicyNumber"
                ],
                "metrics": [
                    "InsuredLoss"
                ]
            }
        ]
    },
    "numberOfRuns": 1000,
    "randomSeed": 1,
    "lossAllocation": {
        "ref": "",  # "LA"
        "portfolio": {
            "ref": ""  # portfolio
        }
    },
    "currency": [
        {
            "code": "usd",
            "rate": 1
        }
    ]
}

# REQUIRED ACTION: Define request as an object (update references)
request_object = LossAllocationRequest()
request_object.set_currency(value=CurrencyTable(name="My currency", currencies=[Currency(code="usd", rate=1)]))
request_object.set_loss_allocation_reference(reference="", portfolio="")
request_object.set_number_of_runs(1000)
request_object.set_random_seed(1)
request_object.add_csv_export(
    characteristics=["ScenarioId", "PolicyNumber"],
    metrics=["InsuredLoss"],
    export_type="simulation"
)

# Run calculations (using dictionary, file, object)
result_1 = list(client.calculations().loss_allocation(request=request))
result_2 = list(client.calculations().loss_allocation(request="./data/training_request.json"))
result_3 = list(client.calculations().loss_allocation(request=request_object.get()))

for row in result_1:
    print(row)
