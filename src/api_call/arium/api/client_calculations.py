import codecs
import csv
import json
import logging.config
from typing import TYPE_CHECKING, Dict, Union

import requests

from constants import *

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from api_call.client import APIClient


class CalculationsClient:
    SUBJECT = {
        "la-export": ENDPOINT_CALC_LA_EXPORT,
        "la": ENDPOINT_CALC_LA,
        "perturbations": ENDPOINT_PERTURBATIONS,
    }

    def __init__(self, api_client: 'APIClient'):
        self.api_client = api_client

    def loss_allocation(self, request_file: str = None, request: Dict = None):
        yield from self._loss_allocation(request_file, request, subject="la")

    def loss_allocation_export(self, request_file: str = None, request: Dict = None):
        yield from self._loss_allocation(request_file, request, subject="la-export")

    def perturbations(self, request_file: str = None, request: Dict = None):
        yield from self._loss_allocation(request_file, request, subject="perturbations")

    def _loss_allocation(self, request_file: str = None, request: Dict = None, loss_allocation_id: str = "la",
                         subject: str = "la"):
        logger.info("Loss allocation")

        data = {"id": loss_allocation_id, "description": loss_allocation_id, "headers": True}
        la = self.SUBJECT[subject]
        response = self._upload("/{{tenant}}/{la}/".format(la=la), data, request=request, request_file=request_file)

        logger.debug("Response: {}".format(response))

        csv_export = subject != "la"
        yield from self._get_response_data(response, csv_export)

    def exposures(self, request_file: str = None, request: Dict = None):
        logger.info("Loss allocation - exposures")
        yield from self._asynchronous_endpoint_csv(ENDPOINT_CALC_EXPOSURES, request_file, request)

    def node_metrics(self, request_file: str = None, request: Dict = None, portfolio: str = None, raw=False):
        if portfolio is None:
            logger.info("Node metrics")
            return self._synchronous_endpoint_put(ENDPOINT_NODE_METRICS, request_file, request, raw)

        logger.info("Node metrics - calculations")
        endpoint = ENDPOINT_CALC_NODE_METRICS.format(portfolio=portfolio)
        return self._asynchronous_endpoint(endpoint, request_file, request, raw)

    def connected_nodes(self, request_file: str = None, request: Dict = None, portfolio: str = None, raw=False):
        logger.info("Connected nodes")
        endpoint = ENDPOINT_CALC_CONNECTED_NODES.format(portfolio=portfolio)
        return self._asynchronous_endpoint(endpoint, request_file, request, raw)

    def dictionary(self, request_file: str = None, request: Dict = None, raw=False):
        logger.info("Dictionary")
        return self._synchronous_endpoint_put(ENDPOINT_DICTIONARY, request_file, request, raw)

    def properties(self, request_file: str = None, request: Dict = None, raw=False):
        logger.info("Properties")
        return self._synchronous_endpoint_put(ENDPOINT_PROPERTIES, request_file, request, raw)

    def la_params(self, request_file: str = None, request: Dict = None, portfolio: str = None):
        logger.info("LA params")
        endpoint = ENDPOINT_CALC_LA_PARAMETERS.format(portfolio=portfolio)
        return self._asynchronous_endpoint_csv(endpoint, request_file, request)

    def programmes(self, raw=False):
        logger.info("Programmes")
        return self._synchronous_endpoint_get(ENDPOINT_PROGRAMMES, raw)

    def portfolio_download(self, request_file: str = None, request: Dict = None, portfolio: str = None):
        logger.info("Portfolio download")
        endpoint = ENDPOINT_PORTFOLIO_DOWNLOAD.format(portfolio=portfolio)
        return self._asynchronous_endpoint_csv(endpoint, request_file, request)

    def _asynchronous_endpoint(self, endpoint: str, request_file: str = None, request: Dict = None, raw=False):
        url = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
        response = self._upload(url, {}, request_file=request_file, request=request)
        return next(self._get_response_data(response, raw=raw))

    def _asynchronous_endpoint_csv(self, endpoint: str, request_file: str = None, request: Dict = None):
        url = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
        response = self._upload(url, {}, request_file=request_file, request=request)
        yield from self._get_response_data(response, True)

    def _synchronous_endpoint_put(self, endpoint: str, request_file: str = None, request: Dict = None, raw=False):
        endpoint = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
        request = self._get_request_data(request_file, request, read_json=True)
        result = self.api_client.put_request(endpoint, json=request)
        return result if raw else json.loads(result.content)

    def _synchronous_endpoint_get(self, endpoint: str, raw=False):
        endpoint = "/{{tenant}}/{endpoint}".format(endpoint=endpoint)
        result = self.api_client.get_request(endpoint)
        return result if raw else json.loads(result.content)

    @staticmethod
    def _get_request_data(request_file: str = None, request: Dict = None, read_json=False):
        if request is not None:
            if read_json:
                return request
            request = json.dumps(request)
        elif request_file is not None:
            if read_json:
                with open(request_file) as f:
                    request = json.load(f)
            else:
                with open(request_file, 'rb') as f:
                    request = f.read()
        else:
            raise Exception("'request_file' or 'request' argument is required!")
        return request

    def _upload(self, url: str, data: Dict, request_file: str = None, request: Dict = None) -> Union[Dict, None]:
        response = self.api_client.get_data(self.api_client.put_request(url, json=data))
        upload_url = response['url']
        status_location = '/' + response['location']
        request = self._get_request_data(request_file, request)

        upload_response = requests.put(url=upload_url,
                                       data=request,
                                       headers={'Content-Type': ''})

        logger.debug("Upload response code: {}".format(upload_response.status_code))
        return self.api_client.pooling(status_location, self.api_client.get_data)

    def _get_response_data(self, response, csv_output=False, raw=False):
        urls = response['urls'] if 'urls' in response else [response['url']]
        for url in urls:
            if csv_output:
                with requests.get(url) as response:
                    reader = csv.reader(codecs.iterdecode(response.content.splitlines(), 'utf-8'))
                    for row in reader:
                        yield row
            else:
                with requests.get(url) as response:
                    yield response if raw else self.api_client.get_data(response)
