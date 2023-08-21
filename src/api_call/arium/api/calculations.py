import json
import re
from http import HTTPStatus
from typing import Dict, TYPE_CHECKING, Union

import requests

from api_call.arium.api.request import (
    get_content,
    get_request_data,
    calc_polling,
    get_content_from_url,
)
from config.constants import ENDPOINT_CALC_LA, ENDPOINT_PERTURBATIONS
from config.get_logger import get_logger

if TYPE_CHECKING:
    from api_call.client import APIClient

logger = get_logger(__name__)


class Calculations:
    SUBJECT = {
        "la": ENDPOINT_CALC_LA,
        "perturbations": ENDPOINT_PERTURBATIONS,
    }

    def __init__(self, subject: str = "la"):
        self.subject = subject
        self.data = {}
        self.presigned = None
        self.id = None
        self.location = None
        self.upload_response = None
        self.results_urls = []

    def _get_presigned_upload(self, client: "APIClient", url: str):
        try:
            response = client.put_request(endpoint=url, json=self.data)
            content = get_content(response=response, get_from_location=False)
            upload_url = content.get("url", None)
            if upload_url is None:
                raise Exception("Operation is not supported on this environment!")
        except Exception as e:
            logger.error("Cannot get presigned url.")
            raise e

        self.location = "/" + content["location"]
        self.id = self.location.split("/")[-1]

        logger.debug(f"Presigned url: {upload_url}")
        logger.info(f"Location: {self.location}")
        logger.info(f"Calculations id: {self.id}")

        return upload_url

    def upload_request(
        self,
        client: "APIClient",
        request: Union[Dict, str],
        presigned: bool = True,
        request_args: Dict = None,
    ):
        self.presigned = presigned
        self.subject = self.SUBJECT.get(self.subject, self.subject)

        request = get_request_data(request=request, request_args=request_args)
        if presigned:
            request = json.dumps(request)

        endpoint = f"/{{tenant}}/{self.subject}"

        logger.debug(f"Upload request for subject '{self.subject}' with presigned.")

        if presigned:
            self.upload_response = requests.put(
                url=self._get_presigned_upload(client=client, url=endpoint),
                data=request,
                headers={"Content-Type": ""},
                verify=False,
            )
        else:
            self.upload_response = client.put_request(endpoint=endpoint, json=request)

        logger.debug(f"Upload response code: {self.upload_response.status_code}")

    def is_ready(self, client: "APIClient"):
        response = client.get_request(self.location)
        return response.status_code != HTTPStatus.ACCEPTED

    def pooling(self, client: "APIClient"):
        if self.presigned:
            response = calc_polling(client=client, endpoint=self.location)
            content = get_content(response=response)

            self.results_urls = content.get("urls", [content["url"]])

        return self

    def get_results(self, csv_output: bool = True, raw: bool = False):
        if self.presigned:
            for url in self.results_urls:
                result = get_content_from_url(url=url, csv_output=csv_output, raw=raw)
                yield next(result) if raw else result
        else:
            if raw:
                yield self.upload_response
            else:
                yield json.loads(self.upload_response.content)
