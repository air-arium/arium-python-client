from typing import TYPE_CHECKING, Dict, Union

from api_call.arium.api.calculations import Calculations
from api_call.arium.api.request import get_resources, get_content, get_content_from_url
from config.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from api_call.client import APIClient


class RefDataClient:
    def __init__(self, client: "APIClient"):
        self.client = client

    def get(self, ref_name: str):
        endpoint = f"/refdata/{ref_name}"
        response = self.client.get_request(endpoint=endpoint)
        content = get_content(response=response)

        logger.info(f"Received reference data for {ref_name}.")
        return content

