from datetime import datetime

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Create request (update references)
request = {
    "export": {
        "csv": [
            {
                "type": "simulation",
                "characteristics": [
                    "PolicyType",
                    "ScenarioId",
                    "PolicyNumber"
                ],
                "metrics": [
                    "InsuredLoss",
                    "EconomicLoss",
                    "DefenceCost",
                    "NonEconomicLoss",
                    "AggregatesDamaged",
                    "AccountId",
                    "UniquePolicyId"
                ]
            }
        ]
    },
    "numberOfRuns": 1000,
    "randomSeed": 1,
    "lossAllocation": {
        "ref": "",
        "portfolio": {
            "ref": ""
        }
    },
    "currency": {
        "ref": ""
    }
}

# We can use this request to call loss allocation or perturbations and measure time.
before = datetime.utcnow()

# Model: default (loss allocation)
result = client.calculations().loss_allocation(request=request)

# Model: perturbations
# result_perturbations = list(client.calculations().perturbations(request=request))

print('Calculations took ' + str(datetime.utcnow() - before))

# Get first export (iterate over result to get all exports if multiple were defined in the request)
export_0 = next(result)

# Result is csv export file. First row is the header:
export_0 = list(export_0)
header = export_0[0]
rows = export_0[1:]

print(f"Export header: {header}")
print(f"Number of rows: {len(rows)}")
