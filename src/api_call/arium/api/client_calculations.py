from typing import TYPE_CHECKING, Dict, Union

from api_call.arium.api.calculations import Calculations
from config.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from api_call.client import APIClient


class CalculationsClient:
    SUBJECT = {
        "la": ENDPOINT_CALC_LA,
        "perturbations": ENDPOINT_PERTURBATIONS,
    }

    def __init__(self, client: 'APIClient'):
        self.client = client

    def loss_allocation(self, request: Union[str, Dict], csv_output=True):
        result = self._calculate_presigned(
            subject='la',
            request=request,
            csv_output=csv_output,
        )

        if csv_output:
            yield from result
        else:
            result = next(next(result))
            yield result

    def perturbations(self, request: Union[str, Dict]):
        yield from self._calculate_presigned(
            subject="perturbations",
            request=request,
        )

    def _calculate_presigned(self, subject: str, request: Union[str, Dict],
                             csv_output: bool = True, raw: bool = False, presigned=True):
        """
        Note: This is a generator. From multiple presigned links.
        """
        logger.info(f"Endpoint (generator): {subject}, presigned={presigned}, raw={raw}, csv_output={csv_output}")

        results = self.get_calculations(
            request=request,
            subject=subject,
            presigned=presigned,
        ).pooling(client=self.client).get_results(csv_output=csv_output, raw=raw)

        yield from results

    def _calculate_simple(self, subject: str, request: Union[str, Dict],
                          csv_output: bool = True, raw: bool = False, presigned: bool = False):
        """
        Note: This function returns value. From content or one presigned link.
        """
        logger.info(f"Endpoint: {subject}, presigned={presigned}, raw={raw}, csv_output={csv_output}")

        results = self.get_calculations(
            request=request,
            subject=subject,
            presigned=presigned,
        ).pooling(self.client).get_results(csv_output=csv_output, raw=raw)

        return next(results)

    def get_calculations(self, request: Union[str, Dict], subject: str = "la", presigned: bool = True) -> Calculations:
        calculations = Calculations(subject)
        calculations.upload_request(
            client=self.client,
            request=request,
            presigned=presigned
        )
        return calculations

    def node_metrics(self, request: Union[str, Dict], portfolio: str = None, raw=False):

        if portfolio is None:
            subject = ENDPOINT_NODE_METRICS
            presigned = False
        else:
            subject = ENDPOINT_CALC_NODE_METRICS.format(portfolio=portfolio)
            presigned = True

        return self._calculate_simple(
            request=request,
            subject=subject,
            presigned=presigned,
            raw=raw
        )

    def connected_nodes(self, request: Union[str, Dict], portfolio: str = None, raw=False):
        return self._calculate_simple(
            request=request,
            subject=ENDPOINT_CALC_CONNECTED_NODES.format(portfolio=portfolio),
            presigned=True,
            raw=raw,
        )

    def dictionary(self, request: Union[str, Dict], raw=False):
        return self._calculate_simple(
            request=request,
            subject=ENDPOINT_DICTIONARY,
            raw=raw,
        )

    def properties(self, request: Union[str, Dict], raw=False):
        return self._calculate_simple(
            request=request,
            subject=ENDPOINT_PROPERTIES,
            raw=raw,
        )

    def la_params(self, request: Union[str, Dict], portfolio: str = None):
        return self._calculate_simple(
            request=request,
            subject=ENDPOINT_CALC_LA_PARAMETERS.format(portfolio=portfolio),
            presigned=True
        )

    def programmes(self, raw=False):
        return self._calculate_simple(
            request={},
            subject=ENDPOINT_PROGRAMMES,
            raw=raw
        )

    def portfolio_download(self, request: Union[str, Dict], portfolio: str = None):
        return self._calculate_simple(
            subject=ENDPOINT_PORTFOLIO_DOWNLOAD.format(portfolio=portfolio),
            request=request,
            presigned=True,
        )
