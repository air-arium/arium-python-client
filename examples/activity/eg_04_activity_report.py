from api_call.arium.model.activity import Report
from api_call.client import APIClient
from auth.okta_auth import Auth


def main():
    # TODO - provide authorization settings - see README.md for details
    auth_settings = {}

    # Perform authentication
    auth = Auth(tenant="test", role="basic", settings=auth_settings)

    # Create the new client - it will execute the required API actions
    client = APIClient(auth=auth)

    # The first step is to get the activity details
    # TODO - provide activity id
    report: Report | None = client.activity().report("<your_activity_id>")


    if report is None:
        print("No report found for this activity.")
        exit(1)

    # TODO - provide report name of your choice. It is zip file so leave .zip extension
    report_name = "report.zip"
    # Download the report
    report.download(report_name)

    print(f"Report saved to file: {report_name}")

    # Display the content of the report
    print(f"Content of {report_name}:")
    for filename, content in report.files():
        print(filename)


if __name__ == "__main__":
    main()
