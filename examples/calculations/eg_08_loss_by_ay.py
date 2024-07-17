import csv
import json
import os

from api_call.arium.util.currency_table import Currency, CurrencyTable
from api_call.arium.util.analysis_request import (
    AnalysisRequest,
    AnalysisAsset,
)
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace2", role="basic", settings=auth_settings)
client = APIClient(auth=auth)

business_as_usual = True
# REQUIRED ACTION: Set output folder path
output_folder = "output/"

# REQUIRED ACTION: Set ref ids

# Select saved event set id
a_id = "example-asset-reference"

# Select portfolio id
portfolio_id = "example-portfolio-reference"

# Create request
request_object = AnalysisRequest()

# set Loss by Accidental Year for the existing asset
asset_object = AnalysisAsset(**json.loads(client.analysis().get_data(asset_id=a_id)))
asset_object.set_loss_by_ay(True)
asset = client.analysis().create("loss by AY", data=asset_object.get())

request_object.set_analysis_reference(reference=asset["id"], portfolio=portfolio_id)

currency_eur = Currency(code="EUR", rate=1.0)
currency_table = CurrencyTable(name="CurrencyTable", currencies=[currency_eur])
request_object.set_currency(currency_table)

request_object.add_csv_export(
    export_type="simulation", characteristics=["ScenarioId"], metrics=["GrossLoss"]
)

"""
Advanced run - with downloading traceability files
"""

# Run calculations

result = client.calculations().get_calculations_asset(
    request=request_object.get(),
    name="A_AY",
)

# Wait for results
client.calculations().asset().wait(asset_id=result["id"])

# Check status
print(result)

# Print report
report = client.calculations().report(asset_id=result["id"])
if report:
    for row in report:
        print(row)


# Function that saves claims to local files
def save_csv(folder, name, report):
    if not os.path.exists(folder):
        os.makedirs(folder)

    for part, claims_part in enumerate(report):
        claims_rows = list(claims_part)

        with open(f"{folder}/{name}_{part}.csv", "w", newline="") as f:
            csv.writer(f).writerows(claims_rows)


def save_text(folder, name, extension, report, json_output=False):
    if not os.path.exists(folder):
        os.makedirs(folder)

    for number, data in enumerate(report):
        with open(folder + f"{name}_{number}.{extension}", "w") as f:
            if json_output:
                json.dump(data, f, indent=4)
            else:
                f.write(data)


# Get raw claims
# report = client.service().get_raw_claims(result["id"])
# save_csv(f"{output_folder}raw_claims", "claims", report)

# Get processed claims
# level = "AggLayerId"  # (or 'EntityId' or 'TreatyId')
# report = client.service().get_processed_claims(result["id"], level)
# save_csv(f"{output_folder}processed_claims_{level}", "claims", report)


# try:
#     # Get logs
#     # currently we generate logs only for graph processing (part of map step)
#     level = "map"
#     report = client.service().get_logs(result["id"])
#     save_text(f"{output_folder}log/{level}/", "claims_log", "log", report)
# except Exception as e:
#     print(e)
#     print("You must define traceability parameters in the request first.")
