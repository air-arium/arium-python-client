import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from api_call.arium.api.client_assets import AssetsClient

class TestAssetsClient(unittest.TestCase):
    def setUp(self):
        self.mock_api_client = MagicMock()
        self.mock_api_client.get_workspace.return_value = "test-tenant"
        self.collection = "test-collection"
        self.client = AssetsClient(self.mock_api_client, self.collection)

    def test_list_assets(self):
        mock_assets = [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}]
        with patch('api_call.arium.api.client_assets.request.asset_list', return_value=mock_assets):
            assets = self.client.list()
            self.assertEqual(assets, mock_assets)

    def test_get_asset(self):
        asset_id = "123"
        mock_asset = {"id": asset_id, "name": "Test"}
        with patch('api_call.arium.api.client_assets.request.asset_get', return_value=mock_asset):
            asset = self.client.get(asset_id)
            self.assertEqual(asset, mock_asset)

    def test_create_asset(self):
        asset_name = "New Asset"
        data = {"key": "val"}
        mock_created = {"id": "new-id", "name": asset_name}
        with patch('api_call.arium.api.client_assets.request.asset_post', return_value=mock_created):
            created = self.client.create(asset_name, data)
            self.assertEqual(created, mock_created)

    def test_delete_asset(self):
        asset_id = "123"
        with patch('api_call.arium.api.client_assets.request.asset_delete') as mock_del:
            self.client.delete(asset_id)
            mock_del.assert_called_once_with(client=self.mock_api_client, collection=self.collection, asset_id=asset_id)

if __name__ == '__main__':
    unittest.main()
