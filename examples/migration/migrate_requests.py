import json
import os

"""
Migrate you requests to match v16 schema
1. Add requests to "requests" folder.
2. Run script.
3. Updated requests will be saved to "requests_updated" folder.
"""


def parse_occurrence(value):
    if "settings" in value:
        occurrence_type = value["settings"].pop("type")
        if occurrence_type:
            if occurrence_type == 1:
                raise ValueError("'CoinFlip' event sampling is deprecated for v1.16.")
            return {
                "frequency": float(value["settings"].pop("probability")),
                "equalWeighted": True,
            }
    s = {
        "frequency": value.pop("frequency") if "frequency" in value else None,
        "freqParamKey": value.pop("freqParamKey") if "freqParamKey" in value else None,
        "equalWeighted": value.pop("equalWeighted")
        if "equalWeighted" in value
        else None,
    }
    return {k: v for k, v in s.items() if v is not None}


folder = "requests/"
for file in os.listdir(folder):
    with open(folder + file) as f:
        data = json.load(f)

    print(f"Updating {file}...")

    groups = []
    print(f"\tUpdating groups.")
    if "ref" not in data["lossAllocation"]:
        for _, group in data["lossAllocation"].items():
            try:
                if "groupName" in group:
                    group["title"] = group.pop("groupName")

                if "connected" in group:
                    del group["connected"]

                settings = parse_occurrence(group)
                group["settings"] = settings
                groups.append(group)
            except ValueError as e:
                print(f"\tException: {e}")
            except Exception as e:
                print(e)

        data["lossAllocation"] = {"groups": groups}

    if not os.path.exists("requests_updated/"):
        os.makedirs("requests_updated/")

    with open("requests_updated/" + file, "w") as f:
        print("\tSaving.")
        json.dump(data, f, indent=2)
