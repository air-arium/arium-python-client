import csv

from api_call.arium.util.loss_allocation_request import LossAllocationRequest
from api_call.client import APIClient
from auth.okta_auth import Auth
from config.constants import CLIENT_ID, CLIENT_SECRET, AUTH_SERVER, ISSUER, AUDIENCE

prefix = ""
settings = {}

# Create new client
auth = Auth(
    tenant="workspace1",
    role="basic",
    settings=settings,
    prefix=prefix,
    verify=False,
)
client = APIClient(auth=auth)

# Select loss allocation id
la_id = ""

# Select portfolio id
portfolio_id = ""

# Select currency table id
currency_table_id = ""

# Create request
request = LossAllocationRequest()
request.set_loss_allocation_reference(reference=la_id, portfolio=portfolio_id)
request.set_currency_reference(currency_table_id)
request.set_number_of_runs(100)
request.set_random_seed(1)
request.set_total_loss(on=True)
request.add_csv_export(
    export_type="simulation",
    characteristics=["ScenarioId"],
    metrics=[
        "EconomicLoss",
        "DefenceCost",
        "NonEconomicLoss",
        "PolicyNumber",
        "GrossLoss",
    ],
)

# Run calculations
result = client.calculations().loss_allocation(request=request.get())
with open("output_total_loss.csv", "w", newline="") as f:
    csv.writer(f).writerows(*result)
