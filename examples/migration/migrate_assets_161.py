import json
import os


"""
Migrate you assets to match v16.1 schema
1. Add assets to "assets" folder.
2. Run script.
3. Updated assets will be saved to "assets_updated" folder.
"""
create_events = True

default_params = {
    "lossByAY": False,
    "businessAsUsual": False,
    "perturbations": False,
}


def parse(param, field):
    if param not in field:
        print(f"Setting default {param}...")
        field[param] = default_params[param]


if not os.path.exists("updated/"):
    os.makedirs("updated/")

if not os.path.exists("updated/assets/"):
    os.makedirs("updated/assets/")

if not os.path.exists("updated/events/"):
    os.makedirs("updated/events/")

folder = "assets/"

for file in os.listdir(folder):
    with open(folder + file) as f:
        data = json.load(f)

    print(f"Updating {file}...")

    settings = data["settings"]

    for k in default_params.keys():
        parse(k, settings)

    if create_events:
        groups = data["groups"]
        for group in groups:
            for i, event in enumerate(group["scenarios"]):
                if "ref" not in event:
                    _folder = file.replace(".json", "")
                    if not os.path.exists(f"updated/events/{_folder}/"):
                        os.makedirs(f"updated/events/{_folder}/")

                    with open(
                        f"updated/events/{_folder}/" + event["title"],
                        "w",
                    ) as f:
                        print(f"\tSaving event {event['title']}.")
                        event.pop("id", None)
                        if "author" not in event:
                            event["author"] = ""
                        if "timestamp" not in event:
                            event["timestamp"] = 0
                        if "mapExpandedNaics" not in event["scenario"]:
                            event["scenario"]["mapExpandedNaics"] = []

                        if event["scenario"].get("multiSelectedNodeId"):
                            raise Exception(
                                f"Not empty! "
                                f"event['scenario']['multiSelectedNodeId']="
                                f"{event['scenario']['multiSelectedNodeId']}"
                            )
                        event["scenario"]["multiSelectedNodeId"] = []
                        json.dump(event, f, indent=2)

                    group["scenarios"][i] = {
                        "title": event["title"],
                        "ref": f"{_folder}/{event['title']}",
                    }

    file = file.replace("json", "")
    with open("updated/assets/" + file, "w") as f:
        print(f"\tSaving LA {file}.")
        json.dump(data, f, indent=2)
