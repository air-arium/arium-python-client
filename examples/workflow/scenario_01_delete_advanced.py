from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
# Note: please set <PREFIX>_CLIENT_ID, <PREFIX>_CLIENT_SECRET
prefix = ""
settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=settings, prefix=prefix)
client = APIClient(auth=auth)

# Print the client info
print(client)

# Get list of scenarios
scenarios = client.scenarios().list()


def is_scenario_in_folder(reference, folder):
    """
    Checks if the scenario is located in given folder.
    :param reference: scenario reference
    :param folder: folder name (may include sub-folders)
    :return: True if scenario is located in folder otherwise False
    """
    return reference.startswith("{folder}/".format(folder=folder))


# Print all scenarios in "2021 Q3" folder
for scenario in scenarios:
    name = scenario["name"]
    if is_scenario_in_folder(name, "2021 Q3"):
        # You can remove the scenario here:
        # delete_scenario(client, ref)
        pass  # Currently just skip

# Another way to get scenarios from "2021 Q3" folder
s_2021_Q3_folder = [
    scenario["id"]
    for scenario in scenarios
    if is_scenario_in_folder(scenario["name"], "2021 Q3")
]

# Get all scenarios with "Q3" in name (folder or name itself)
s_Q3 = [scenario["id"] for scenario in scenarios if "Q3" in scenario["name"]]

# Get all scenarios with "Air" in name from "test" folder - you can filter the scenarios with multiple conditions
s_Air = [
    scenario["id"]
    for scenario in scenarios
    if "Air" in scenario["name"] and is_scenario_in_folder(scenario["name"], "test")
]

# Print the scenarios from s_Air list
for scenario_ref in s_Air:
    print(scenario_ref)

# Delete all scenarios from s_Air list (you can use any list you want!)
for scenario_ref in s_Air:
    if client.scenarios().delete(scenario_ref):
        print("{ref} removed successfully!".format(ref=scenario_ref))
