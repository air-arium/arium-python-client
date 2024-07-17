import json

from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}


# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)


# REQUIRED ACTION: Set path to sizes request file
# Define request
request_file = "path/to/sizes_request.json"

# Define size data
size_data_file = "data/size/sizes.csv"
size_data_quadrupled_file = "data/size/sizes_quadruple.csv"
size_data_thresholds_file = "data/size/sizes_thresholds.csv"
size_data_quadrupled_thresholds_file = "data/size/sizes_thresholds_quadruple.csv"

# Upload size data (if not uploaded yet)
files = [
    size_data_file,
    size_data_quadrupled_file,
    size_data_thresholds_file,
    size_data_quadrupled_thresholds_file,
]
list_sizes = client.sizes().list()
list_sizes_names = [s["name"] for s in list_sizes]

for file in files:
    name = file.split("/")[-1].replace(".csv", "")
    if name not in list_sizes_names:
        client.sizes().create(asset_name=name, file=file)

sizes = {s["name"]: s["id"] for s in client.sizes().list()}

# Read the basic request
with open(request_file) as f:
    request = json.load(f)

# Create request with first size data and run calculations
request1 = request.copy()
# Base size data, no thresholds:
request1["sizeData"] = {"ref": sizes["sizes"]}
result1 = client.calculations().analysis(request=request1)
report1 = client.calculations().report(asset_id=result1["id"])

# Create request with second size data and run calculations
request2 = request.copy()
# same as request1['sizeData'] but all size metrics quadrupled:
request2["sizeData"] = {"ref": sizes["sizes_quadruple"]}
result2 = client.calculations().analysis(request=request2)
report2 = client.calculations().report(asset_id=result2["id"])

# Create request with third size data and run calculations
request3 = request.copy()
# Base size data, with thresholds
request3["sizeData"] = {"ref": sizes["sizes_thresholds"]}
result3 = client.calculations().analysis(request=request3)
report3 = client.calculations().report(asset_id=result3["id"])

# Create request with fourth size data and run calculations
request4 = request.copy()
# same as request3['sizeData'] but all size metrics quadrupled:
request4["sizeData"] = {"ref": sizes["sizes_thresholds_quadruple"]}
result4 = client.calculations().analysis(request=request4)
report4 = client.calculations().report(asset_id=result4["id"])


# print all the results
for report in [report1, report2, report3, report4]:
    if report:
        print(f"Report ID: {report['id']}")
        for row in report:
            print(row)
