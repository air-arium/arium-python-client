import logging.config
from typing import Dict, Tuple

from requests import Response

from api_call.arium.api.client_assets import PortfoliosClient, ScenariosClient, SizesClient, ProgrammesClient, \
    CurrencyTablesClient, LAsClient, AssetsClient
from api_call.arium.api.client_calculations import CalculationsClient
from auth.okta_auth import Auth
from config.constants import *


class APIClient:
    def __init__(self, auth: Auth):
        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)
        self._auth = auth
        self._assets_clients = {
            COLLECTION_PORTFOLIOS: PortfoliosClient(self),
            COLLECTION_SCENARIOS: ScenariosClient(self),
            COLLECTION_LAS: LAsClient(self),
            COLLECTION_CURRENCY_TABLES: CurrencyTablesClient(self),
            COLLECTION_PROGRAMMES: ProgrammesClient(self),
            COLLECTION_SIZES: SizesClient(self),
        }
        self._calculations_client = CalculationsClient(self)
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

    def assets(self, collection: str) -> AssetsClient:
        return self._assets_clients[collection]

    def portfolios(self) -> PortfoliosClient:
        return self._assets_clients[COLLECTION_PORTFOLIOS]

    def scenarios(self) -> ScenariosClient:
        return self._assets_clients[COLLECTION_SCENARIOS]

    def loss_allocations(self) -> LAsClient:
        return self._assets_clients[COLLECTION_LAS]

    def currency_tables(self) -> CurrencyTablesClient:
        return self._assets_clients[COLLECTION_CURRENCY_TABLES]

    def programmes(self) -> ProgrammesClient:
        return self._assets_clients[COLLECTION_PROGRAMMES]

    def sizes(self) -> SizesClient:
        return self._assets_clients[COLLECTION_SIZES]

    def calculations(self) -> CalculationsClient:
        return self._calculations_client

    def _format_endpoint(self, endpoint: str) -> str:
        return endpoint.format(tenant=self._auth.tenant)

    def _get_default(self, url: str, headers: Dict, plain: bool = False) -> Tuple[str, Dict]:
        if url is None:
            url = self._auth.connections()[BASE_URI]
        if headers is None:
            headers = {"Content-Type": "text/plain"} if plain else {"Content-Type": "application/json; charset=utf-8"}
        return url, headers

    def _request(self, method: str, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        url, headers = self._get_default(url, headers, 'data' in kwargs)
        endpoint = self._format_endpoint(endpoint)
        url += endpoint
        self.logger.debug(f"method: {method} url: {url} headers: {headers}")
        return self.method_fun[method](url=url, headers=headers, verify=self._auth.verify, **kwargs)

    def get_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("GET", endpoint, url, headers, **kwargs)

    def post_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("POST", endpoint, url, headers, **kwargs)

    def put_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("PUT", endpoint, url, headers, **kwargs)

    def delete_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("DELETE", endpoint, url, headers, **kwargs)
