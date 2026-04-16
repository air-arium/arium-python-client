from api_call.arium.model.activity import ActivitySubmitRequest, ActivityPayloadModel, ActivityType, ActivityMode, OutputItem, OutputItemParameters, \
    OutputExportType, OutputProjection, OutputPerspective, ActivityStatus
from api_call.arium.model.simulation import SimulationModel, LossAllocation
from api_call.client import APIClient
from auth.okta_auth import Auth


def main():
    # TODO - provide authorization settings - see README.md for details
    auth_settings = {}

    # Perform authentication
    auth = Auth(tenant="test", role="basic", settings=auth_settings)

    # Create the new client - it will execute the required API actions
    client = APIClient(auth=auth)

    request = ActivitySubmitRequest(
        activityType=ActivityType.CALCULATION,
        mode=ActivityMode.STOCHASTIC,
        # TODO - provide activity name to find it easily in UI
        # name="<your_activity_name>",
        name="Test activity submit stochastic",
        payload=ActivityPayloadModel(
            output=[
                OutputItem(
                    exportType=OutputExportType.AAL,
                    parameters=OutputItemParameters(
                        projections=[OutputProjection.PORTFOLIO],
                        perspectives=[OutputPerspective.ECONOMIC_LOSS, OutputPerspective.NON_ECONOMIC_LOSS, OutputPerspective.DEFENSE_LOSS,
                                      OutputPerspective.GROSS_LOSS]
                    )
                )
            ],
            references=[],
            simulation=SimulationModel(
                lossAllocation=LossAllocation(
                    # TODO - provide id of the loss allocation
                    ref="<your_loss_allocation_id>"
                ),
            )
        )
    )

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


if __name__ == "__main__":
    main()
