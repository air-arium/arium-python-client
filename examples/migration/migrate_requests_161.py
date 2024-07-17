import json
import os

"""
Migrate you requests to match v16.1 schema
1. Add requests to "requests" folder.
2. Run script.
3. Updated requests will be saved to "requests_updated" folder.
"""

# Parameters moved from request to asset
asset_params = [
    "minimumGroundup",
    "numberOfRuns",
    "randomSeed",
    "perturbations",
    "lossByAY",
    "businessAsUsual",
    "portfolioReferenceYear",
    "bulkSetEqualWeighted",
]
# Input path
requests_path = "requests/"

# Path where assets will be saved
updated_path = "updated/"
assets_path = f"assets/"
updated_request_path = f"{updated_path}/requests/"

if not os.path.exists(updated_path):
    os.makedirs(updated_path)

if not os.path.exists(assets_path):
    os.makedirs(assets_path)

if not os.path.exists(updated_request_path):
    os.makedirs(updated_request_path)


for file in os.listdir(requests_path):
    with open(requests_path + file) as f:
        request = json.load(f)

    print(f"Updating {file}...")

    if "ref" not in request["lossAllocation"]:
        asset = request.pop("lossAllocation")
        name = file.replace(".json", "")

        # Name should be replaced with reference after asset creation
        request["lossAllocation"] = {"ref": name}
        asset["settings"] = {}

        # Create assets - embedded assets are no longer supported
        for param in asset_params:
            if param in request:
                asset["settings"][param] = request[param]

        with open(assets_path + name, "w") as f:
            print("\tSaving.")
            json.dump(asset, f, indent=2)

    # Remove parameters
    for param in asset_params:
        if param in request:
            del request[param]

    with open(updated_request_path + file, "w") as f:
        print("\tSaving.")
        json.dump(request, f, indent=2)
