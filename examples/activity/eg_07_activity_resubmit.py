from api_call.client import APIClient
from auth.okta_auth import Auth

def main():
    # REQUIRED ACTION: Set settings
    auth_settings = {}

    # Perform authentication
    auth = Auth(tenant="test", role="basic", settings=auth_settings)

    # Create the new client - it will execute the required API actions
    client = APIClient(auth=auth)

    # Resubmit activity based on Canceled activity
    activity_id = client.activity().resubmit(activity_id='<canceled_activity_id>')
    print(f"Activity resubmitted successfully. New activity id: {activity_id}")


if __name__ == "__main__":
    main()
