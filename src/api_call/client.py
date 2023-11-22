from typing import Dict, Tuple

from requests import Response

from api_call.arium.api.client_assets import (
    PortfoliosClient,
    ScenariosClient,
    SizesClient,
    ProgrammesClient,
    CurrencyTablesClient,
    LAsClient,
    AssetsClient,
)
from api_call.arium.api.client_calculations import CalculationsClient
from api_call.arium.api.pdca_client import PDCAClient
from api_call.arium.api.client_refdata import RefDataClient
from auth.okta_auth import Auth
from config.constants import *
from config.get_logger import get_logger

logger = get_logger(__name__)


class APIClient:
    def __init__(self, auth: Auth):
        self._auth = auth

        self._assets_clients = None
        self._calculations_client = None
        self._pdca_client = None
        self._refdata_client = None

        if BASE_URI in self._auth.settings():
            self._assets_clients = {
                COLLECTION_PORTFOLIOS: PortfoliosClient(self),
                COLLECTION_SCENARIOS: ScenariosClient(self),
                COLLECTION_LAS: LAsClient(self),
                COLLECTION_CURRENCY_TABLES: CurrencyTablesClient(self),
                COLLECTION_PROGRAMMES: ProgrammesClient(self),
                COLLECTION_SIZES: SizesClient(self),
            }
            self._calculations_client = CalculationsClient(self)
            self._refdata_client = RefDataClient(self)

        if BASE_URI_PDCA in self._auth.settings():
            self._pdca_client = PDCAClient(self)

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

    def get_pdca(self):
        if self._pdca_client:
            return self._pdca_client
        raise Exception(
            f"PDCA client was not initialized. "
            f"Reason: {BASE_URI_PDCA} wasn't defined. "
            f"Specify the '{BASE_URI_PDCA}' "
            f"or '{AUDIENCE}' and '{AUDIENCE_PDCA}' in auth settings."
        )

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

    def scenarios(self) -> ScenariosClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_SCENARIOS]

    def loss_allocations(self) -> LAsClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_LAS]

    def currency_tables(self) -> CurrencyTablesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_CURRENCY_TABLES]

    def programmes(self) -> ProgrammesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_PROGRAMMES]

    def sizes(self) -> SizesClient:
        self._checks_client()
        return self._assets_clients[COLLECTION_SIZES]

    def calculations(self) -> CalculationsClient:
        self._checks_client()
        return self._calculations_client

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
        return self.method_fun[method](
            url=url, headers=headers, verify=self._auth.verify, **kwargs
        )

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
