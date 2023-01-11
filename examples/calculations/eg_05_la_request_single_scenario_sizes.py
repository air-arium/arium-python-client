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

# REQUIRED ACTION: Select ids
portfolio_id = ""
scenario_id = ""
size_data_id = ""
currency_id = ""

# Create request
request = LossAllocationRequest()
request.add_scenario_reference(
    reference=scenario_id,
    scenario_id="Scenario 0",
    key=0,
    group_name="Group 0",
    portfolio=portfolio_id
)
request.set_currency_reference(currency_id)
request.set_number_of_runs(100)
request.set_random_seed(1)
request.set_size_data(size_data_id)
request.add_csv_export(
    export_type='simulation',
    characteristics=['ScenarioId'],
    metrics=['GrossLoss', 'EconomicLoss', "AccountId", "UniquePolicyId"]
)
request_dict = request.get()

# Run calculations
result = client.calculations().loss_allocation(request=request_dict)

# Display
for export in result:
    for row in export:
        print(row)
