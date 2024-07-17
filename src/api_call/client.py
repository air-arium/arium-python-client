from typing import Dict, Tuple

from requests import Response

from api_call.arium.api.client_assets import (
    PortfoliosClient,
    EventsClient,
    SizesClient,
    ProgrammesClient,
    CurrencyTablesClient,
    AnalysesClient,
    AssetsClient,
)
from api_call.arium.api.client_calculations import CalculationsClient
from api_call.arium.api.client_calculations_asset import CalculationsAssetClient
from api_call.arium.api.client_refdata import RefDataClient
from api_call.arium.api.request import retry
from auth.okta_auth import Auth
from config.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)


class APIClient:
    def __init__(self, auth: Auth):
        self._auth = auth

        self._assets_clients = None
        self._calculations_client = None
        self._calculations_asset_client = None
        self._refdata_client = None

        if BASE_URI in self._auth.settings():
            self._assets_clients = {
                COLLECTION_PORTFOLIOS: PortfoliosClient(self),
                COLLECTION_EVENTS: EventsClient(self),
                COLLECTION_ANALYSES: AnalysesClient(self),
                COLLECTION_CURRENCY_TABLES: CurrencyTablesClient(self),
                COLLECTION_PROGRAMMES: ProgrammesClient(self),
                COLLECTION_SIZES: SizesClient(self),
            }
            self._calculations_client = CalculationsClient(self)
            self._calculations_asset_client = CalculationsAssetClient(self)

        self.method_fun = {
            "GET": self._auth.client.get,
            "DELETE": self._auth.client.delete,
            "PUT": self._auth.client.put,
            "POST": self._auth.client.post,
        }

    def __repr__(self) -> str:
        return self._auth.__repr__()

    def __str__(self) -> str:
        return self._auth.__repr__()

    @property
    def verify(self):
        return self._auth.verify

    def get_workspace(self):
        return self._auth.tenant

    def _checks_client(self):
        if not self._assets_clients:
            raise Exception(
                f"Arium client was not initialized. "
                f"Reason: ARIUM {BASE_URI} wasn't defined. "
                f"Specify the '{BASE_URI}' or '{AUDIENCE}' in auth settings."
            )

    def refdata(self) -> RefDataClient:
        return self._refdata_client

    def assets(self, collection: str) -> AssetsClient:
        self._checks_client()
        return self._assets_clients[collection]

    def portfolios(self) -> PortfoliosClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_PORTFOLIOS]

    def events(self) -> EventsClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_EVENTS]

    def analysis(self) -> AnalysesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_ANALYSES]

    def currency_tables(self) -> CurrencyTablesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_CURRENCY_TABLES]

    def programmes(self) -> ProgrammesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_PROGRAMMES]

    def sizes(self) -> SizesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_SIZES]

    def service(self) -> CalculationsClient:
        self._checks_client()
        return self._calculations_client

    def calculations(self) -> CalculationsAssetClient:
        self._checks_client()
        return self._calculations_asset_client

    def _format_endpoint(self, endpoint: str) -> str:
        return endpoint.format(tenant=self._auth.tenant)

    def _get_default(
        self, url: str, headers: Dict, plain: bool = False
    ) -> Tuple[str, Dict]:
        if url is None:
            url = self._auth.settings()[BASE_URI]
        elif url in self._auth.settings():
            url = self._auth.settings()[url]

        if headers is None:
            headers = (
                {"Content-Type": "text/plain"}
                if plain
                else {"Content-Type": "application/json; charset=utf-8"}
            )
        return url, headers

    @retry(times=10)
    def _request(
        self,
        method: str,
        endpoint: str,
        url: str = None,
        headers: Dict = None,
        **kwargs,
    ) -> Response:
        url, headers = self._get_default(url, headers, "data" in kwargs)
        endpoint = self._format_endpoint(endpoint)
        url += endpoint
        logger.debug(f"method: {method} url: {url} headers: {headers}")
        response = self.method_fun[method](
            url=url, headers=headers, verify=self._auth.verify, **kwargs
        )
        response.close()
        return response

    def get_request(
        self, endpoint: str, url: str = None, headers: Dict = None, **kwargs
    ) -> Response:
        return self._request("GET", endpoint, url, headers, **kwargs)

    def post_request(
        self, endpoint: str, url: str = None, headers: Dict = None, **kwargs
    ) -> Response:
        return self._request("POST", endpoint, url, headers, **kwargs)

    def put_request(
        self, endpoint: str, url: str = None, headers: Dict = None, **kwargs
    ) -> Response:
        return self._request("PUT", endpoint, url, headers, **kwargs)

    def delete_request(
        self, endpoint: str, url: str = None, headers: Dict = None, **kwargs
    ) -> Response:
        return self._request("DELETE", endpoint, url, headers, **kwargs)
