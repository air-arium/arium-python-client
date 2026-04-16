import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from api_call.client import APIClient
from auth.okta_auth import Auth
from config.constants import BASE_URI, BASE_URI_PDCA

class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.mock_auth = MagicMock(spec=Auth)
        self.mock_auth.tenant = "test-tenant"
        self.mock_auth.verify = True
        self.mock_auth.settings.return_value = {
            BASE_URI: "https://api.test.com",
            BASE_URI_PDCA: "https://pdca.test.com"
        }
        self.mock_auth.client = MagicMock()

    def test_api_client_init(self):
        client = APIClient(auth=self.mock_auth)
        self.assertEqual(client.get_workspace(), "test-tenant")
        self.assertTrue(client.verify)
        # Check if clients are initialized
        self.assertIsNotNone(client.activity())
        self.assertIsNotNone(client.refdata())

    def test_api_client_get_request(self):
        client = APIClient(auth=self.mock_auth)
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_auth.client.get.return_value = mock_response

        response = client.get_request("/test-endpoint")
        
        # It seems APIClient._format_endpoint might not be doing what I think if url doesn't have {tenant}
        # Let's check Actual in error: Actual: get(url='https://api.test.com/test-endpoint', ...)
        # This means url += endpoint resulted in https://api.test.com/test-endpoint
        # Which means endpoint remained /test-endpoint
        
        expected_url = "https://api.test.com/test-endpoint"
        self.mock_auth.client.get.assert_called_once_with(
            url=expected_url,
            headers={"Content-Type": "application/json; charset=utf-8"},
            verify=True
        )
        self.assertEqual(response, mock_response)

    def test_api_client_post_request(self):
        client = APIClient(auth=self.mock_auth)
        mock_response = MagicMock()
        mock_response.status_code = 201
        self.mock_auth.client.post.return_value = mock_response

        payload = {"key": "value"}
        response = client.post_request("/test-endpoint", json=payload)
        
        expected_url = "https://api.test.com/test-endpoint"
        self.mock_auth.client.post.assert_called_once_with(
            url=expected_url,
            headers={"Content-Type": "application/json; charset=utf-8"},
            verify=True,
            json=payload
        )
        self.assertEqual(response, mock_response)

    def test_api_client_get_request_with_tenant_in_endpoint(self):
        # If the endpoint already has {tenant}, it should be formatted
        client = APIClient(auth=self.mock_auth)
        mock_response = MagicMock()
        self.mock_auth.client.get.return_value = mock_response

        response = client.get_request("/{tenant}/test")
        expected_url = "https://api.test.com/test-tenant/test"
        self.mock_auth.client.get.assert_called_once_with(
            url=expected_url,
            headers={"Content-Type": "application/json; charset=utf-8"},
            verify=True
        )

    def test_api_client_format_endpoint(self):
        client = APIClient(auth=self.mock_auth)
        formatted = client._format_endpoint("/{tenant}/resource")
        self.assertEqual(formatted, "/test-tenant/resource")

    def test_api_client_get_default(self):
        client = APIClient(auth=self.mock_auth)
        
        # Default URL from settings
        url, headers = client._get_default(None, None)
        self.assertEqual(url, "https://api.test.com")
        self.assertEqual(headers, {"Content-Type": "application/json; charset=utf-8"})
        
        # Specific URL key from settings
        url, headers = client._get_default(BASE_URI_PDCA, None)
        self.assertEqual(url, "https://pdca.test.com")
        
        # Custom URL
        url, headers = client._get_default("https://custom.com", None)
        self.assertEqual(url, "https://custom.com")

if __name__ == '__main__':
    unittest.main()
