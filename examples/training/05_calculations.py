from api_call.arium.model.activity import ActivitySubmitRequest, ActivityPayloadModel, ActivityType, ActivityMode, \
    OutputItem, OutputItemParameters, OutputExportType, OutputProjection, OutputPerspective, ActivityStatus
from api_call.arium.model.simulation import SimulationModel, LossAllocation, CurrencyItem, PortfolioRef
from api_call.client import APIClient
from auth.okta_auth import Auth

# REQUIRED ACTION: Set settings
auth_settings = {}

# Create new client
auth = Auth(tenant="workspace1", role="basic", settings=auth_settings)
client = APIClient(auth=auth)
print(client)

# REQUIRED ACTION: Set request parameters
# Define request as a dictionary
# This structure matches ActivitySubmitRequest.to_dict()
request_dict = {
    "activityType": "calculation",
    "mode": "stochastic",
    "name": "Training Calculation - Dictionary",
    "payload": {
        "output": [
            {
                "exportType": "aal",
                "parameters": {
                    "projections": ["portfolio"],
                    "perspectives": ["economicLoss"]
                }
            }
        ],
        "simulation": {
            "lossAllocation": {
                "ref": "example-asset-reference",
                "portfolio": {"ref": "example-portfolio-reference"},
            },
            "currency": [{"code": "usd", "rate": 1}],
        }
    }
}

# REQUIRED ACTION: Set request object parameters
# Define request as an object
request_object = ActivitySubmitRequest(
    activityType=ActivityType.CALCULATION,
    mode=ActivityMode.STOCHASTIC,
    name="Training Calculation - Object",
    payload=ActivityPayloadModel(
        output=[
            OutputItem(
                exportType=OutputExportType.AAL,
                parameters=OutputItemParameters(
                    projections=[OutputProjection.PORTFOLIO],
                    perspectives=[OutputPerspective.ECONOMIC_LOSS]
                )
            )
        ],
        simulation=SimulationModel(
            lossAllocation=LossAllocation(
                ref="example-asset-reference",
                portfolio=PortfolioRef(ref="example-portfolio-reference"),
            ),
            currency=[CurrencyItem(code="usd", rate=1)]
        )
    )
)

# REQUIRED ACTION: select which method of submitting analysis should be used
# Submit calculations (using: 1: dictionary, 2: file, 3: object)

# method 1: dictionary
# ActivitySubmitRequest.from_dict can be used to convert dictionary to request object
request_1 = ActivitySubmitRequest.from_dict(request_dict)
activity_1 = client.activity().submit(request_1)
print(f"Activity 1 submitted: {activity_1.activityId}")

# method 2: json file (simulated here)
# request_2 = ActivitySubmitRequest.from_json("path/to/request.json")
# activity_2 = client.activity().submit(request_2)

# method 3: object
activity_3 = client.activity().submit(request_object)
print(f"Activity 3 submitted: {activity_3.activityId}")

# Wait for activity to complete and get results
# This is a common pattern for the new Activity client
try:
    print("Waiting for Activity 3 to complete...")
    completed_activity = client.activity().wait(activity_3.activityId, timeout_minutes=10)
    print(f"Activity status: {completed_activity.status.value}")

    if completed_activity.status == ActivityStatus.COMPLETED:
        # Access reports
        report = completed_activity.report()
        if report:
            print(f"Report available: {report.file}")
            # You can download it: report.download("results.zip")
            # Or list files in it:
            for filename, content in report.files():
                print(f" - Found file in report: {filename}")
        else:
            print("No report found.")
    elif completed_activity.status == ActivityStatus.FAILED:
        print(f"Activity failed with error: {completed_activity.errors}")

except Exception as e:
    print(f"Error while waiting for activity: {e}")
