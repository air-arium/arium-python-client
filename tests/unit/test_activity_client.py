import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from api_call.arium.api.client_activity import ActivityClient
from api_call.arium.model.activity import Activity, ActivityStatus, ActivitySubmitRequest

class TestActivityClient(unittest.TestCase):
    def setUp(self):
        self.mock_api_client = MagicMock()
        self.client = ActivityClient(self.mock_api_client)

    def test_get_activity(self):
        activity_id = "test-id"
        mock_response_data = {
            "activityId": activity_id,
            "workspace": "test-workspace",
            "name": "test-activity",
            "status": "completed"
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_api_client.get_request.return_value = mock_response
        
        with patch('api_call.arium.api.client_activity.get_content', return_value=mock_response_data):
            activity = self.client.get(activity_id)
            
        self.mock_api_client.get_request.assert_called_once_with(
            endpoint=f"/{{tenant}}/activity/{activity_id}",
            retry=1
        )
        self.assertIsInstance(activity, Activity)
        self.assertEqual(activity.activityId, activity_id)
        self.assertEqual(activity.status, ActivityStatus.COMPLETED)

    def test_submit_activity(self):
        request = MagicMock(spec=ActivitySubmitRequest)
        request.to_dict.return_value = {"payload": "data"}
        
        mock_submit_response = {"data": {"activityId": "new-id"}}
        mock_activity_data = {
            "activityId": "new-id", 
            "status": "queued",
            "workspace": "test-workspace",
            "name": "test-activity"
        }
        
        mock_response = MagicMock()
        self.mock_api_client.post_request.return_value = mock_response
        
        # We need to patch get_content because it's used inside submit
        with patch('api_call.arium.api.client_activity.get_content', return_value=mock_submit_response):
            # Also need to mock self.get() which is called at the end of submit
            with patch.object(ActivityClient, 'get') as mock_get:
                mock_get.return_value = Activity.from_dict(mock_activity_data)
                activity = self.client.submit(request)
                
                self.mock_api_client.post_request.assert_called_once()
                mock_get.assert_called_once_with(activity_id="new-id")
                self.assertEqual(activity.activityId, "new-id")

    def test_cancel_activity(self):
        activity_id = "test-id"
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_api_client.post_request.return_value = mock_response
        
        self.client.cancel(activity_id)
        
        self.mock_api_client.post_request.assert_called_once_with(
            endpoint=f"/{{tenant}}/activity/{activity_id}/cancel"
        )

if __name__ == '__main__':
    unittest.main()
