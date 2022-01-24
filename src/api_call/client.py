import logging.config
from http.client import HTTPException
from typing import Callable, Dict, Union

from requests import Response

from api_call.arium.api.request import calc_pooling
from api_call.arium.api.client_assets import PortfoliosClient, ScenariosClient, SizesClient, ProgrammesClient, \
    CurrencyTablesClient, LAsClient
from api_call.arium.api.client_calculations import CalculationsClient
from auth.okta_auth import Auth
from constants import *

global_client = None


class APIClient:
    def __init__(self, auth: Auth):
        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)
        self._auth = auth
        self._assets_clients = {
            COLLECTION_SCENARIOS: ScenariosClient(self),
            COLLECTION_PORTFOLIOS: PortfoliosClient(self),
            COLLECTION_SIZES: SizesClient(self),
            COLLECTION_PROGRAMMES: ProgrammesClient(self),
            COLLECTION_CURRENCY_TABLES: CurrencyTablesClient(self),
            COLLECTION_LAS: LAsClient(self),
        }
        self._calculations_client = CalculationsClient(self)
        self.method_fun = {
            "GET": self._auth.client.get,
            "DELETE": self._auth.client.delete,
            "PUT": self._auth.client.put,
            "POST": self._auth.client.post,
        }

    def assets(self, collection: str):
        return self._assets_clients[collection]

    def scenarios(self):
        return self._assets_clients[COLLECTION_SCENARIOS]

    def portfolios(self):
        return self._assets_clients[COLLECTION_PORTFOLIOS]

    def programmes(self):
        return self._assets_clients[COLLECTION_PROGRAMMES]

    def sizes(self):
        return self._assets_clients[COLLECTION_SIZES]

    def las(self):
        return self._assets_clients[COLLECTION_LAS]

    def currency_tables(self):
        return self._assets_clients[COLLECTION_CURRENCY_TABLES]

    def calculations(self):
        return self._calculations_client

    def __repr__(self):
        return self._auth.__repr__()

    def __str__(self):
        return self._auth.__repr__()

    def _format_endpoint(self, endpoint: str) -> str:
        return endpoint.format(tenant=self._auth.tenant)

    def _get_default(self, url, headers, plain=False):
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

    def post_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("POST", endpoint, url, headers, **kwargs)

    def get_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("GET", endpoint, url, headers, **kwargs)

    def put_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("PUT", endpoint, url, headers, **kwargs)

    def delete_request(self, endpoint: str, url: str = None, headers: Dict = None, **kwargs) -> Response:
        return self._request("DELETE", endpoint, url, headers, **kwargs)

    def get_data(self, response: Response) -> [Dict, None]:
        parsed_response = {}
        self.logger.debug(response.status_code)

        if response.status_code == 200:
            self.logger.debug(response.headers["Content-Type"])

            try:
                import json
                parsed_response = json.loads(response.text)
            except Exception as e:
                self.logger.debug(e)
                return parsed_response

        elif response.status_code == 202:
            return None

        else:
            self.logger.error("Status code: {}".format(response.status_code))
            try:
                import json
                d = json.loads(response.content)
            except Exception as e:
                self.logger.debug(e)
                raise HTTPException(response.content) from None
            raise HTTPException(d)

        return parsed_response

    def pooling(self, endpoint: str, response_collector: Callable[[Response], Dict]):
        return calc_pooling(self, endpoint, response_collector)


def set_client(client: APIClient):
    global global_client
    global_client = client


def get_client() -> Union[None, APIClient]:
    global global_client
    return global_client
