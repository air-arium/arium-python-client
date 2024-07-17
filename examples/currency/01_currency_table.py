import json

from api_call.arium.util.currency_table import Currency, CurrencyTable
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

# Create dictionaries representing currencies
currency_1 = Currency(code="USD", rate=1)
currency_2 = Currency(code="EUR", rate=1.2)
currency_3 = Currency(code="GBP", rate=0.98)

# Create dictionary representing currency table
currency_list = [currency_1, currency_2, currency_3]
currency_table_name = "My currency"
currency_table = CurrencyTable(name=currency_table_name, currencies=currency_list)

# Create currency table resource
asset_data = client.currency_tables().create(
    asset_name=currency_table_name, data=currency_table.get()
)
print(f"currency table: {json.dumps(asset_data, indent=4)}")
