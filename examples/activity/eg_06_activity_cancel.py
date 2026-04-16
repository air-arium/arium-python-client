from api_call.arium.model.activity import ActivitySubmitRequest, ActivityPayloadModel, ActivityType, ActivityMode, OutputItem, OutputItemParameters, \
    OutputExportType, OutputProjection, OutputPerspective
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

    # Create activity submit request
    request = ActivitySubmitRequest(
        activityType=ActivityType.CALCULATION,
        mode=ActivityMode.STOCHASTIC,
        # TODO - provide activity name to find it easily in UI
        # name="<your_activity_name>",
        name="Test activity",
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
    # submit activity
    activity = client.activity().submit(request)

    print(f"Activity {activity.activityId} has been submitted with status: {activity.status.value}")

    # cancel activity
    client.activity().cancel(activity.activityId)

    print(f"Activity {activity.activityId} has been cancelled")

    # get activity status - it should be in status CANCELLED
    activity = client.activity().get(activity.activityId)
    print(f"Activity {activity.activityId} has status: {activity.status.value}")


if __name__ == "__main__":
    main()
