from api_call.arium.model.activity import Report, ActivitySubmitRequest, ActivityPayloadModel, ActivityType, ActivityMode, OutputItem, OutputItemParameters, \
    OutputExportType, OutputProjection, OutputPerspective, ActivityStatus, Activity
from api_call.client import APIClient
from auth.okta_auth import Auth


def main():
    # TODO - provide authorization settings - see README.md for details
    auth_settings = {}

    # Perform authentication
    auth = Auth(tenant="test", role="basic", settings=auth_settings)

    # Create the new client - it will execute the required API actions
    client = APIClient(auth=auth)

    # Create activity submit request:
    #   activityType: ActivityType.LOSS_EXPORT
    #   references: provide id of the stochastic simulation where the results are stored
    #   payload - define output - what projections and perspectives to export

    request = ActivitySubmitRequest(
        activityType=ActivityType.LOSS_EXPORT,
        mode=ActivityMode.STOCHASTIC,
        # TODO - provide activity name to find it easily in UI
        # name="<your_activity_name>",
        name="Test loss export activity",
        payload=ActivityPayloadModel(
            output=[
                OutputItem(
                    exportType=OutputExportType.AAL,
                    parameters=OutputItemParameters(
                        projections=[OutputProjection.INDUSTRY],
                        perspectives=[OutputPerspective.ECONOMIC_LOSS, OutputPerspective.NON_ECONOMIC_LOSS, OutputPerspective.DEFENSE_LOSS,
                                      OutputPerspective.GROSS_LOSS]
                    )
                )
            ],
            # TODO - provide id of the existing activity of type 'calculation' (ActivityType.CALCULATION) - called parent activity
            references=["<your_parent_activity_id>"]
        )
    )

    activity: Activity | None = None

    try:
        activity = client.activity().submit(request)
        print(f"Activity {activity.activityId} has been submitted with status: {activity.status.value}")

        # Wait for activity to complete. Increase timeout if needed
        activity = client.activity().wait(activity.activityId, timeout_minutes=60)
        print(f"Activity {activity.activityId} has been completed with status: {activity.status.value}")

        if activity.status == ActivityStatus.FAILED:
            print(f"Activity failed with error: {activity.errors}")

    except Exception as e:
        print(f"Activity submission failed with error: {e}")

    report: Report | None = client.activity().report(activity.activityId)

    if report is None:
        print("No report found for this activity.")
        exit(1)

    # TODO - provide report name of your choice. It is zip file so leave .zip extension
    report_name = "report.zip"
    report.download(report_name)
    print(f"Report saved to file: report.zip")


if __name__ == "__main__":
    main()
