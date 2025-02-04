import json
import re
import time
from http import HTTPStatus
from typing import Dict, TYPE_CHECKING, Union

import requests

from api_call.arium.api.request import (
    get_content,
    get_data,
    calc_polling,
    get_content_from_url,
    retry,
)
from config.get_logger import get_logger

if TYPE_CHECKING:
    from api_call.client import APIClient

logger = get_logger(__name__)


class Calculations:
    def __init__(self):
        self.data = {}
        self.presigned = None
        self.id = None
        self.location = None
        self.upload_response = None
        self.results_urls = []
        self.traceability_id = None
        self.name = None

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

    @retry(times=10)
    def upload_request(
        self,
        client: "APIClient",
        request: Union[Dict, str],
        endpoint: str,
        presigned: bool = True,
        name: str = None,
    ):
        if name is None:
            self.name = f"loss-allocation-{time.strftime('%Y-%m-%d-%H-%M-%S')}"

        self.presigned = presigned
        self.subject = self.SUBJECT.get(self.subject, self.subject)

        request = get_data(request=request)
        if presigned:
            request = json.dumps(request)

        endpoint = f"/{{tenant}}/{endpoint.format(name=self.name)}"

        logger.debug(f"Upload request with presigned.")

        if presigned:
            self.upload_response = requests.put(
                url=self._get_presigned_upload(client=client, url=endpoint),
                data=request,
                headers={"Content-Type": ""},
                verify=False,
            )
            self.upload_response.close()
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

            try:
                r = rf"calculation.Result./{client.get_workspace()}/(.*?)/"
                self.traceability_id = re.search(r, self.results_urls[-1]).group(1)
                logger.info(f"Traceability id: {self.traceability_id}")
            except AttributeError:
                pass

        return self

    def get_results(
        self, csv_output: bool = True, raw: bool = False, verify: bool = True
    ):
        if self.presigned:
            for url in self.results_urls:
                result = get_content_from_url(
                    url=url, csv_output=csv_output, raw=raw, verify=verify
                )
                yield next(result) if raw else result
        else:
            if raw:
                yield self.upload_response
            else:
                yield json.loads(self.upload_response.content)
