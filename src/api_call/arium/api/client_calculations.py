from typing import TYPE_CHECKING, Dict, Union

from api_call.arium.api.calculations import Calculations
from api_call.arium.api.calculations_asset import CalculationsAsset
from api_call.arium.api.request import get_resources, get_content, get_content_from_url
from config.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from api_call.client import APIClient


class CalculationsClient:
    def __init__(self, client: "APIClient"):
        self.client = client

    def get_claims(self, calculations_id: str, level: str):
        supported = ("AggLayerId", "EntityId", "TreatyId", "raw")

        if level not in supported:
            raise ValueError(
                f"Level '{level}' is not supported. Please select one of: {supported}"
            )

        return get_resources(
            client=self.client,
            calculations_id=calculations_id,
            endpoint=ENDPOINT_CLAIMS.format(level=level),
            delimiter="|",
        )

    def get_logs(self, calculations_id: str):
        resources = get_resources(
            client=self.client,
            calculations_id=calculations_id,
            endpoint=ENDPOINT_LOGS,
            csv_output=False,
        )

        for r, g in resources:
            yield r, next(g)

    def _calculate_presigned(
        self,
        request: Union[str, Dict],
        endpoint: str,
        csv_output: bool = True,
        raw: bool = False,
        presigned=True,
    ):
        """
        Note: This is a generator. From multiple presigned links.
        """
        logger.info(
            f"Endpoint (generator): endpoint={endpoint}, presigned={presigned}, raw={raw}, csv_output={csv_output}"
        )

        results = (
            self.get_calculations(
                request=request,
                presigned=presigned,
                endpoint=endpoint,
            )
            .pooling(client=self.client)
            .get_results(csv_output=csv_output, raw=raw, verify=self.client.verify)
        )

        yield from results

    def _calculate_simple(
        self,
        request: Union[str, Dict],
        endpoint: str,
        csv_output: bool = True,
        raw: bool = False,
        presigned: bool = False,
    ):
        """
        Note: This function returns value. From content or one presigned link.
        """
        logger.info(
            f"Endpoint: endpoint={endpoint}, presigned={presigned}, raw={raw}, csv_output={csv_output}"
        )

        results = (
            self.get_calculations(
                request=request,
                presigned=presigned,
                endpoint=endpoint,
            )
            .pooling(self.client)
            .get_results(csv_output=csv_output, raw=raw)
        )

        return next(results)

    def get_calculations(
        self,
        request: Union[str, Dict],
        endpoint: str,
        presigned: bool = True,
    ) -> Calculations:
        calculations = Calculations()
        calculations.upload_request(
            client=self.client,
            request=request,
            presigned=presigned,
            endpoint=endpoint,
        )
        return calculations

    def node_metrics(self, request: Union[str, Dict], portfolio: str = None, raw=False):
        if portfolio is None:
            endpoint = ENDPOINT_NODE_METRICS
            presigned = False
        else:
            endpoint = ENDPOINT_CALC_NODE_METRICS.format(portfolio=portfolio)
            presigned = True

        return self._calculate_simple(
            request=request, endpoint=endpoint, presigned=presigned, raw=raw
        )

    def connected_nodes(
        self, request: Union[str, Dict], portfolio: str = None, raw=False
    ):
        return self._calculate_simple(
            request=request,
            endpoint=ENDPOINT_CALC_CONNECTED_NODES.format(portfolio=portfolio),
            presigned=True,
            raw=raw,
        )

    def dictionary(self, request: Union[str, Dict], raw=False):
        return self._calculate_simple(
            request=request,
            endpoint=ENDPOINT_DICTIONARY,
            raw=raw,
        )

    def properties(self, request: Union[str, Dict], raw=False):
        return self._calculate_simple(
            request=request,
            endpoint=ENDPOINT_PROPERTIES,
            raw=raw,
        )

    def analysis_params(self, request: Union[str, Dict], portfolio: str = None):
        return self._calculate_simple(
            request=request,
            endpoint=ENDPOINT_CALC_ANALYSIS_PARAMETERS.format(portfolio=portfolio),
            presigned=True,
        )

    def programmes(self, raw=False):
        return self._calculate_simple(request={}, endpoint=ENDPOINT_PROGRAMMES, raw=raw)

    def portfolio_download(self, request: Union[str, Dict], portfolio: str = None):
        return self._calculate_simple(
            endpoint=ENDPOINT_PORTFOLIO_DOWNLOAD.format(portfolio=portfolio),
            request=request,
            presigned=True,
        )
