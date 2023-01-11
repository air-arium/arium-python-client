import csv
import json

from api_call.arium.util.currency_table import Currency, CurrencyTable
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set connections
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
connections = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", connections=connections, prefix=prefix)
client = APIClient(auth=auth)

# REQUIRED ACTION: Define assets
currency_table_name = 'c1'
currency_file = './data/currency/currency.csv'

portfolio_name = '362'
portfolio_file = './data/portfolio/362.csv'

la_name = 'AllHistoricalScenarios 2021-Q3'
la_file = './data/la/AllHistoricalScenarios 2021-Q3.json'

# Request (define export)
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
    "lossAllocation": {},
    "currency": {}
}


def create_portfolio(portfolio_name, portfolio_filepath):
    # Open file and read data
    with open(portfolio_filepath) as f:
        data = f.read()

    # API call to create portfolio
    portfolio = client.portfolios().create(portfolio_name, data)

    # Portfolio is a dictionary with portfolio parameters
    # Get id (reference) from this dictionary
    return portfolio['id']


def create_currency(currency_name, currency_file):
    # Open file and read data
    with open(currency_file) as f:
        currency_data = csv.reader(f)

        # Ignore header
        next(currency_data)

        # Create list of currencies
        currency_list = [Currency(code=c, rate=float(r)) for c, r in currency_data]

    # Create currency table
    currency_table = CurrencyTable(name=currency_name, currencies=currency_list)

    # Create currency table resource
    return client.currency_tables().create(asset_name=currency_table_name, data=currency_table.get())['id']


# Get list of portfolio names
portfolios = {p['name']: p['id'] for p in client.portfolios().list()}
if portfolio_name not in portfolios:
    # Create portfolio (only if does not exist yet)
    portfolio_id = create_portfolio(portfolio_name, portfolio_file)
else:
    # Portfolio exists, read the id
    portfolio_id = portfolios[portfolio_name]

# Get list of currency names
currencies = {c['name']: c['id'] for c in client.currency_tables().list()}
if currency_file not in currencies:
    # Create currency (only if does not exist yet)
    currency_id = create_currency(currency_table_name, currency_file)
else:
    # Currency exists, read the id
    currency_id = currencies[currency_table_name]

# Get list of las names
las = {c['name']: c['id'] for c in client.loss_allocations().list()}
if la_name not in las:
    # Create la (only if does not exist yet)
    with open(la_file) as file:
        la_id = client.loss_allocations().create(asset_name=la_name, data=file.read(), presigned=True)['id']
else:
    # La exists, read the id
    la_id = las[la_name]

# Update the request
request['lossAllocation']['portfolio'] = {"ref": portfolio_id}
request['currency']['ref'] = currency_id
request['lossAllocation']['ref'] = la_id

# Print the updated request
print(json.dumps(request, indent=4))

# We can use this request to call loss allocation or perturbations
result = list(client.calculations().perturbations(request=request))

# Get first export (iterate over result to get all exports if multiple were defined in the request)
export_0 = next(result)

# Result is csv export file. First row is the header:
export_0 = list(export_0)
header = export_0[0]
rows = export_0[1:]

print(f"Export header: {header}")
print(f"Number of rows: {len(rows)}")
