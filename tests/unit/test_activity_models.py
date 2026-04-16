import unittest
import sys
import os

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from api_call.arium.model.activity import (
    Activity, ActivityStatus, ActivityType, ActivityMode, 
    ActivitySubmitRequest, ActivityPayloadModel, OutputItem,
    OutputItemParameters, OutputExportType, OutputProjection, OutputPerspective
)
from api_call.arium.model.simulation import SimulationModel, LossAllocation

class TestActivityModels(unittest.TestCase):
    def test_activity_from_dict(self):
        data = {
            "activityId": "act-123",
            "workspace": "ws-1",
            "name": "Test Activity",
            "status": "running",
            "activityType": "calculation"
        }
        activity = Activity.from_dict(data)
        self.assertEqual(activity.activityId, "act-123")
        self.assertEqual(activity.status, ActivityStatus.RUNNING)
        self.assertEqual(activity.activityType, ActivityType.CALCULATION)

    def test_activity_to_dict(self):
        activity = Activity(
            activityId="act-123",
            workspace="ws-1",
            name="Test Activity",
            status=ActivityStatus.COMPLETED
        )
        data = activity.to_dict()
        self.assertEqual(data["activityId"], "act-123")
        self.assertEqual(data["status"], "completed")

    def test_activity_submit_request_serialization(self):
        request = ActivitySubmitRequest(
            activityType=ActivityType.CALCULATION,
            mode=ActivityMode.STOCHASTIC,
            name="My Calc",
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
                    lossAllocation=LossAllocation(ref="asset-ref")
                )
            )
        )
        data = request.to_dict()
        self.assertEqual(data["activityType"], "calculation")
        self.assertEqual(data["payload"]["output"][0]["exportType"], "aal")
        self.assertEqual(data["payload"]["output"][0]["parameters"]["projections"], ["portfolio"])
        self.assertEqual(data["payload"]["simulation"]["lossAllocation"]["ref"], "asset-ref")

    def test_activity_submit_request_deserialization(self):
        data = {
            "activityType": "calculation",
            "mode": "stochastic",
            "name": "My Calc",
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
                    "lossAllocation": {"ref": "asset-ref"}
                }
            }
        }
        request = ActivitySubmitRequest.from_dict(data)
        self.assertEqual(request.activityType, ActivityType.CALCULATION)
        self.assertEqual(request.payload.output[0].exportType, OutputExportType.AAL)
        self.assertEqual(request.payload.output[0].parameters.projections[0], OutputProjection.PORTFOLIO)
        self.assertEqual(request.payload.simulation.lossAllocation.ref, "asset-ref")

if __name__ == '__main__':
    unittest.main()
