import logging.config
from typing import TYPE_CHECKING, Dict, Generator, Any, Union

from requests import Response

from api_call.arium.api.request import get_content_from_urls, upload, synchronous_endpoint_get, \
    asynchronous_endpoint_csv, synchronous_endpoint_put, asynchronous_endpoint
from config.constants import *

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

    def __init__(self, client: 'APIClient'):
        self.client = client

    def loss_allocation_boxplot(self, request_file: str = None, request: Dict = None) -> Generator[Any, None, None]:
        logger.info("Loss allocation boxplot")
        yield from self._calculations(request_file=request_file,
                                      request=request,
                                      subject="la")

    def loss_allocation_export(self, request_file: str = None, request: Dict = None) -> Generator[Any, None, None]:
        logger.info("Loss allocation export")
        yield from self._calculations(request_file=request_file,
                                      request=request,
                                      subject="la-export")

    def exposures(self, request_file: str = None, request: Dict = None) -> Generator[Any, None, None]:
        logger.info("Loss allocation - exposures")
        yield from asynchronous_endpoint_csv(client=self.client,
                                             endpoint=ENDPOINT_CALC_EXPOSURES,
                                             request_file=request_file,
                                             request=request)

    def perturbations(self, request_file: str = None, request: Dict = None) -> Generator[Any, None, None]:
        logger.info("Perturbations")
        yield from self._calculations(request_file=request_file,
                                      request=request,
                                      subject="perturbations")

    def _calculations(self, request_file: str = None, request: Dict = None, loss_allocation_id: str = "la",
                      subject: str = "la") -> Generator[Any, None, None]:
        logger.info("Calculations")

        data = {"id": loss_allocation_id, "description": loss_allocation_id, "headers": True}
        csv_output = subject != "la"
        la = self.SUBJECT[subject]

        response = upload(client=self.client,
                          url="/{{tenant}}/{la}/".format(la=la),
                          data=data,
                          request_file=request_file,
                          request=request)
        logger.debug("Response: {}".format(response))
        yield from get_content_from_urls(client=self.client,
                                         response=response,
                                         csv_output=csv_output)

    def node_metrics(self, request_file: str = None, request: Dict = None,
                     portfolio: str = None, raw=False) -> Union[Response, Dict]:
        if portfolio is None:
            logger.info("Node metrics")
            return synchronous_endpoint_put(client=self.client,
                                            endpoint=ENDPOINT_NODE_METRICS,
                                            request_file=request_file,
                                            request=request,
                                            raw=raw)
        else:
            logger.info("Node metrics - calculations")
            return asynchronous_endpoint(client=self.client,
                                         endpoint=ENDPOINT_CALC_NODE_METRICS.format(portfolio=portfolio),
                                         request_file=request_file,
                                         request=request,
                                         raw=raw)

    def connected_nodes(self, request_file: str = None, request: Dict = None, portfolio: str = None, raw=False):
        logger.info("Connected nodes")
        return asynchronous_endpoint(client=self.client,
                                     endpoint=ENDPOINT_CALC_CONNECTED_NODES.format(portfolio=portfolio),
                                     request_file=request_file,
                                     request=request,
                                     raw=raw)

    def dictionary(self, request_file: str = None, request: Dict = None, raw=False):
        logger.info("Dictionary")
        return synchronous_endpoint_put(client=self.client,
                                        endpoint=ENDPOINT_DICTIONARY,
                                        request_file=request_file,
                                        request=request,
                                        raw=raw)

    def properties(self, request_file: str = None, request: Dict = None, raw=False):
        logger.info("Properties")
        return synchronous_endpoint_put(client=self.client,
                                        endpoint=ENDPOINT_PROPERTIES,
                                        request_file=request_file,
                                        request=request,
                                        raw=raw)

    def la_params(self, request_file: str = None, request: Dict = None,
                  portfolio: str = None) -> Generator[Any, None, None]:
        logger.info("LA params")
        return asynchronous_endpoint_csv(client=self.client,
                                         endpoint=ENDPOINT_CALC_LA_PARAMETERS.format(portfolio=portfolio),
                                         request_file=request_file,
                                         request=request)

    def programmes(self, raw=False) -> Union[Response, Dict]:
        logger.info("Programmes")
        return synchronous_endpoint_get(client=self.client,
                                        endpoint=ENDPOINT_PROGRAMMES,
                                        raw=raw)

    def portfolio_download(self, request_file: str = None, request: Dict = None,
                           portfolio: str = None) -> Generator[Any, None, None]:
        logger.info("Portfolio download")
        return asynchronous_endpoint_csv(client=self.client,
                                         endpoint=ENDPOINT_PORTFOLIO_DOWNLOAD.format(portfolio=portfolio),
                                         request_file=request_file,
                                         request=request)
