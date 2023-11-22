import json
import os

"""
Migrate you assets to match v16 schema
1. Add assets to "assets" folder.
2. Run script.
3. Updated assets will be saved to "assets_updated" folder.
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
    return {}


folder = "assets/"
for file in os.listdir(folder):
    with open(folder + file) as f:
        data = json.load(f)

    print(f"Updating {file}...")

    if "shallowCopied" in data:
        print("\tRemoving 'shallowCopied' parameter.")
        del data["shallowCopied"]

    settings = data["settings"]
    if "occurrence" in settings:
        print("\tRemoving 'occurrence' parameter.")
        del settings["occurrence"]

    for group in data["groups"]:
        try:
            settings = parse_occurrence(group)
            print(f"\tUpdating settings from {group['settings']} to {settings}.")
            group["settings"] = settings
        except ValueError as e:
            print(f"\tException: {e}")

    if not os.path.exists("assets_updated/"):
        os.makedirs("assets_updated/")

    with open("assets_updated/" + file, "w") as f:
        print("\tSaving.")
        json.dump(data, f, indent=2)
