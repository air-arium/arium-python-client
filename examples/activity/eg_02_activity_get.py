from api_call.client import APIClient
from auth.okta_auth import Auth


def main():
    # TODO - provide authorization settings - see README.md for details
    auth_settings = {}

    # Perform authentication
    auth = Auth(tenant="test", role="basic", settings=auth_settings)

    # Create the new client - it will execute the required API actions
    client = APIClient(auth=auth)

    # TODO - provide activity id
    # activity = client.activity().get('<your_activity_id>')
    activity = client.activity().get('3f0d83e1-e572-4b37-b747-881753fa88be')
    print(activity.to_json(indent=4))


if __name__ == "__main__":
    main()
