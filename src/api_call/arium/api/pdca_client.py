from http import HTTPStatus
from typing import TYPE_CHECKING, Dict
from urllib.parse import urlencode

from api_call.arium.api.exceptions import AriumAPACResponseException, handle_exception
from api_call.arium.api.request import get_content, logger, calc_polling
from config.constants import BASE_URI_PDCA

if TYPE_CHECKING:
    from api_call.client import APIClient


class PDCAClient:
    def __init__(self, client: "APIClient"):
        self.client = client

    def get_credits(self):
        response = self.client.get_request(endpoint="/credits", url=BASE_URI_PDCA)
        return get_content(response=response)

    def get_health(self):
        endpoint = "/management/health"
        response = self.client.get_request(endpoint=endpoint, url=BASE_URI_PDCA)
        return get_content(response=response)

    def match(self, inputs: Dict, schema: int = 1):
        logger.info(f"Submit match, schema {schema}")
        try:
            result_location = self._submit(inputs=inputs, schema=schema)
            return self.get_status(result_location=result_location)
        except AriumAPACResponseException as e:
            handle_exception(e)

    def augment(self, inputs: Dict, schema: int = 1):
        logger.info(f"Submit augment, schema {schema}")
        try:
            result_location = self._submit(inputs=inputs, schema=schema, augment=True)
            return self.get_status(result_location=result_location)
        except AriumAPACResponseException as e:
            handle_exception(e)

    def _submit(self, inputs: Dict, schema: int = 1, augment=False):
        logger.debug(f"Submit batch, url_params={schema}")
        url_params = {"schema": schema}
        url_params = urlencode(url_params)
        endpoint = "match" if not augment else "augment"

        response = self.client.post_request(
            endpoint=f"/{endpoint}?{url_params}",
            json=inputs,
            url=BASE_URI_PDCA,
        )

        if response.status_code != HTTPStatus.CREATED:
            logger.info(f"ERROR response.status_code : {response.status_code}")
            logger.info(f"ERROR response.headers : {response.headers}")
            logger.info(f"ERROR response.reason : {response.reason}")
            logger.info(f"ERROR response.content : {response.content}")
            raise AriumAPACResponseException(response)

        location = response.headers["location"]
        logger.debug(f"Result location: {location}")
        return location

    def submit_match(self, inputs: Dict, schema: int = 1):
        return self._submit(inputs=inputs, schema=schema)

    def submit_augment(self, inputs: Dict, schema: int = 1):
        return self._submit(inputs=inputs, schema=schema, augment=True)

    def get_status(self, result_location: str):
        response = calc_polling(
            client=self.client,
            endpoint=result_location,
            url=BASE_URI_PDCA,
        )
        return get_content(response)
