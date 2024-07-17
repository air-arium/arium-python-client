from typing import TYPE_CHECKING, Dict, Union

from api_call.arium.api.calculations import Calculations
from api_call.arium.api.calculations_asset import CalculationsAsset
from api_call.arium.api.request import get_resources, get_content, get_content_from_url
from config.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from api_call.client import APIClient


class CalculationsAssetClient:
    def __init__(self, client: "APIClient"):
        self.client = client
        self._calculations_asset = CalculationsAsset(self.client)

    def asset(self):
        return self._calculations_asset

    def report(self, asset_id: str):
        yield from self.asset().report(asset_id=asset_id)

    def report_zip(self, asset_id: str):
        yield from self.asset().report_binary(asset_id=asset_id)

    def analysis(
        self,
        request: Union[str, Dict],
        name: str = None,
    ):
        return self.calculate(
            request=request,
            name=name,
        )

    def get_calculations_asset(
        self,
        request: Union[str, Dict],
        name: str = None,
    ) -> Dict:
        return self._calculations_asset.start(
            request=request,
            name=name,
        )

    def calculate(
        self,
        request: Union[str, Dict],
        name: str = None,
    ) -> Dict:
        asset_data = self.get_calculations_asset(
            request=request,
            name=name,
        )
        asset_id = asset_data["id"]
        self._calculations_asset.wait(asset_id)
        return self._calculations_asset.get(asset_id=asset_id)
