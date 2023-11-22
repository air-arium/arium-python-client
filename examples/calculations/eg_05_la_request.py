from api_call.arium.util.currency_table import Currency, CurrencyTable
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

# Select ids
portfolio_id = ""
scenario_id = ""
size_data_id = ""
currency_id = ""

# Create request
request = LossAllocationRequest()

# Create groups. Optionally set frequency parameters
group_1 = request.create_group(group_name="Group 1")
group_2 = request.create_group(group_name="Group 2", frequency=0.1)

# Add one or more scenarios to each group. Use group index to assign scenarios to groups
request.add_scenario_reference(
    index=group_1,
    reference=scenario_id,
    portfolio=portfolio_id,
)
request.add_scenario_reference(
    index=group_2, reference=scenario_id, portfolio=portfolio_id
)

# Set currency
request.set_currency_reference(currency_id)

# Alternatively set currency by value
# currency_eur = Currency(code="EUR", rate=1.0)
# currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
# request.set_currency(currency_table)

# Set number of runs and random seed
request.set_number_of_runs(100)
request.set_random_seed(1)

# Define export parameters
request.add_csv_export(
    export_type="simulation",
    characteristics=["RunId", "ScenarioId"],
    metrics=["GrossLoss"],
)

# Optionally set size data
# request.set_size_data(size_data_id)

# Convert request to dictionary
request_dict = request.get()

# Run calculations
result = client.calculations().loss_allocation(request=request_dict)

# Display
for export in result:
    for row in export:
        print(row)
