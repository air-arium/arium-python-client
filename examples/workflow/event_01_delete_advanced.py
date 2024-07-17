from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
prefix = "ARIUM_TEST_WEB"
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings, prefix=prefix)
client = APIClient(auth=auth)

# Print the client info
print(client)

# Get list of events
events = client.events().list()


def is_event_in_folder(reference, folder):
    """
    Checks if the event is located in given folder.
    :param reference: event reference
    :param folder: folder name (may include sub-folders)
    :return: True if event is located in folder otherwise False
    """
    return reference.startswith("{folder}/".format(folder=folder))


# Print all events in "2021 Q3" folder
for event in events:
    name = event["name"]
    if is_event_in_folder(name, "2021 Q3"):
        # You can remove the event here:
        # delete_event(client, ref)
        pass  # Currently just skip

# Another way to get events from "2021 Q3" folder
s_2021_Q3_folder = [
    event["id"] for event in events if is_event_in_folder(event["name"], "2021 Q3")
]

# Get all events with "Q3" in name (folder or name itself)
s_Q3 = [event["id"] for event in events if "Q3" in event["name"]]

# Get all events with "Air" in name from "test" folder - you can filter the events with multiple conditions
s_Air = [
    event["id"]
    for event in events
    if "Air" in event["name"] and is_event_in_folder(event["name"], "test")
]

# Print the events from s_Air list
for event_ref in s_Air:
    print(event_ref)

# Delete all events from s_Air list (you can use any list you want!)
for event_ref in s_Air:
    if client.events().delete(event_ref):
        print("{ref} removed successfully!".format(ref=event_ref))
