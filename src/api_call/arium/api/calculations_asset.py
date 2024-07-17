import io
import time
from typing import Dict, TYPE_CHECKING, Union

from api_call.arium.api.client_assets import AssetsClient
from api_call.arium.api.exceptions import AriumAPACException
from api_call.arium.api.request import (
    get_data,
    asset_list_reports,
    asset_get_report,
)
from config.constants import COLLECTION_CALCULATIONS
from config.get_logger import get_logger

if TYPE_CHECKING:
    from api_call.client import APIClient

logger = get_logger(__name__)


class CalculationsAsset(AssetsClient):
    def __init__(self, client: "APIClient"):
        super().__init__(client, collection=COLLECTION_CALCULATIONS)

    def start(
        self,
        request: Union[Dict, str],
        name: str = None,
        wait: bool = True,
    ):
        data = get_data(request)
        if data["export"].get("csv"):
            for csv_exp in data["export"]["csv"]:
                self.validate_data(csv_exp)

        if name is None:
            name = f"analysis-{time.strftime('%Y-%m-%d-%H-%M-%S')}"

        return self.create(asset_name=name, data=data, wait=wait)

    def wait(self, asset_id: str):
        time.sleep(5.0)
        if not self.is_ready(asset_id):
            self.wait(asset_id)

    def is_ready(self, asset_id: str):
        asset = self.get(asset_id)
        return asset["status"] == "active" or asset["status"] == "error"

    def list_reports(self, asset_id: str):
        return asset_list_reports(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
        )

    def get_type(self, asset_id: str):
        return self.get(asset_id)["collectionParams"]["calculations"]["type"]

    def get_report_file(
        self, asset_id: str, file: str, unzip: bool = True, load: bool = True
    ):
        content = asset_get_report(
            client=self.client,
            collection=self.collection,
            asset_id=asset_id,
            file=file,
            unzip=unzip,
            load=load,
            csv_content=self.get_type(asset_id) != "boxplot",
        )
        return content

    def report(self, asset_id: str):
        asset = self.get(asset_id)

        if asset["status"] == "active":
            files = self.list_reports(asset_id=asset["id"])
            if files:
                for file in files:
                    data = self.get_report_file(asset_id=asset["id"], file=file["file"])
                    if self.get_type(asset_id) == "boxplot":
                        return data
                    for row in data:
                        yield row

    def report_binary(self, asset_id: str):
        asset = self.get(asset_id)

        if asset["status"] == "active":
            files = self.list_reports(asset_id=asset["id"])
            if files:
                for file in files:
                    data = self.get_report_file(
                        asset_id=asset["id"], file=file["file"], unzip=False, load=False
                    )
                    yield io.BytesIO(data)

    def validate_data(self, data: dict) -> None:
        gross_loss = data.get("exportNonZeroGrossLoss", True)
        if not gross_loss:
            if "PolicyNumber" in data.get("characteristics", {}):
                raise AriumAPACException(
                    Exception,
                    "Error: Export characteristic 'PolicyNumber' is not allowed while exportNonZeroGrossLoss=False",
                )
