import time
from datetime import datetime, timezone

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Set request parameters
# Request
request = {
    "export": {
        "csv": [
            {
                "type": "simulation",
                "characteristics": ["PolicyType", "ScenarioId", "PolicyNumber"],
                "metrics": [
                    "InsuredLoss",
                    "EconomicLoss",
                    "DefenceCost",
                    "NonEconomicLoss",
                    "AggregatesDamaged",
                    "AccountId",
                    "UniquePolicyId",
                ],
            }
        ]
    },
    "lossAllocation": {
        "ref": "example-asset-reference",
        "portfolio": {"ref": "example-portfolio-reference"},
    },
    "currency": {"ref": "example-currency-reference"},
}

# We can use this request to call analysis and measure time.
before = datetime.now(timezone.utc)

# Model: default (loss allocation)
result = client.calculations().analysis(request=request)
report = client.calculations().report(asset_id=result["id"])
export_0 = next(report)
print(f"Export headers: {export_0}")
if report:
    print("Rows:")
    for row in report:
        print(row)

print("Calculations took " + str(datetime.now(timezone.utc) - before))
