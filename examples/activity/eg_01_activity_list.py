from api_call.client import APIClient
from auth.okta_auth import Auth


def main():
    auth_settings = {}


    # Perform authentication
    auth = Auth(tenant="test", role="basic", settings=auth_settings)

    # Create the new client - it will execute the required API actions
    client = APIClient(auth=auth)

    # Get activity list
    activity_pages = client.activity().list()
    print(activity_pages.count)

    # Iterate through activities
    for activity in activity_pages.list:
        print(activity.to_json())


if __name__ == "__main__":
    main()
