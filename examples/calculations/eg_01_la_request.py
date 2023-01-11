from api_call.arium.util.currency_table import Currency, CurrencyTable
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

# REQUIRED ACTION: Select loss allocation id
la_id = ""

# REQUIRED ACTION: Select portfolio id
portfolio_id = ""

# Create request
request = LossAllocationRequest()
request.set_loss_allocation_reference(reference=la_id, portfolio=portfolio_id)

currency_eur = Currency(code="EUR", rate=1.0)
currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
request.set_currency(currency_table)
request.set_number_of_runs(10000)
request.set_random_seed(1)
request.add_csv_export(
    export_type='simulation',
    characteristics=['ScenarioId'],
    metrics=['GrossLoss']
)

# Run calculations
result = client.calculations().loss_allocation(request=request.get())

# Display
for export in result:
    for row in export:
        print(row)
