import json
import logging.config
import socket
import sys
import webbrowser
from os import environ, path
from typing import List, Dict, Union

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from config.constants import *


class Auth:
    DEFAULT_CONNECTIONS = {
        PORT: 1410,
        REDIRECT_URI: "http://localhost:{port}/",
        CLIENT_ID: None,
        CLIENT_SECRET: None,
        AUTHORIZATION_URL: None,
        TOKEN_URL: None,
        BASE_URI: None,
    }

    def __init__(self, tenant: str, role: str, connections: Union[Dict, str],
                 authorization_code: bool = True, prefix='', verify: bool = True):
        self.role = role
        self.tenant = tenant
        self._config_path = path.dirname(path.abspath(__file__))
        self.verify = verify
        self.client = None

        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)

        self._connections = self._get_conn(connections, prefix, authorization_code)
        offline_access = authorization_code

        self._auth_user(offline_access, authorization_code)

    def __repr__(self) -> str:
        return self.get_dict().__repr__()

    def __str__(self) -> str:
        return self.get_dict().__str__()

    def connections(self) -> Dict:
        return self._connections.copy()

    def get_dict(self) -> Dict:
        return {
            "tenant": self.tenant,
            "role": self.role,
            "connections": {k: v for k, v in self._connections.items() if k not in ('client_id', 'client_secret')},
        }

    def _get_conn(self, connections: Dict, prefix: str = None, authorization_code: bool = True) -> Dict:
        default_c = Auth.DEFAULT_CONNECTIONS.copy()

        if isinstance(connections, str):
            with open(connections) as f:
                connections = json.load(f)

        if connections is not None:
            default_c.update(connections)

        required_keys = list(Auth.DEFAULT_CONNECTIONS)
        if not authorization_code:
            required_keys.remove(AUTHORIZATION_URL)
            del default_c[AUTHORIZATION_URL]

        if not all(default_c.values()):
            self._conn_from_env(default_c, prefix)
        if not all(default_c.values()):
            self.logger.error("Failed to load the configuration. Configuration must include: {missing}!"
                              .format(missing=', '.join({key for key in required_keys if not default_c[key]})))
            sys.exit(1)

        default_c[REDIRECT_URI] = default_c[REDIRECT_URI].format(port=default_c[PORT])
        return default_c

    @staticmethod
    def _conn_from_env(connections: Dict, prefix: str = None) -> Dict:
        prefix = '' if not prefix else prefix.replace("-", "_") + "_"
        for key in connections:
            connections[key] = environ.get(prefix + key, environ.get(key, connections[key]))
        return connections

    def _auth_user(self, offline_access: bool = True, authorization_code: bool = True):
        if self.client and self.client.authorized:
            return

        scope = None
        if self.tenant is not None and self.role is not None:
            scope = ["tenant/" + self.tenant, "role/" + self.role]
            if offline_access:
                scope.append("offline_access")

        self.client = self._auth_user_web(scope) if authorization_code else self._auth_user_backend(scope)

    def _auth_user_backend(self, scope: List) -> OAuth2Session:
        # Authorization
        client = BackendApplicationClient(client_id=self._connections[CLIENT_ID])
        oauth = OAuth2Session(client=client,
                              scope=scope)

        # Token
        token = oauth.fetch_token(token_url=self._connections[TOKEN_URL],
                                  client_id=self._connections[CLIENT_ID],
                                  client_secret=self._connections[CLIENT_SECRET],
                                  scope=scope)
        client = OAuth2Session(self._connections[CLIENT_ID],
                               token=token,
                               auto_refresh_url=self._connections[TOKEN_URL],
                               auto_refresh_kwargs={'client_id': self._connections[CLIENT_ID],
                                                    'client_secret': self._connections[CLIENT_SECRET]},
                               token_updater=lambda _: self.logger.debug("Updated token."))

        return client

    def _auth_user_web(self, scope: List) -> OAuth2Session:
        # Authorization
        client = OAuth2Session(self._connections[CLIENT_ID],
                               redirect_uri=self._connections[REDIRECT_URI],
                               scope=scope)
        url, state = client.authorization_url(url=self._connections[AUTHORIZATION_URL])
        self.logger.debug("Authorization URL: {}".format(url))
        code = self._parse_response(str(self._wait_for_response(url)))

        # Token
        token = client.fetch_token(self._connections[TOKEN_URL],
                                   code=code,
                                   client_secret=self._connections[CLIENT_SECRET],
                                   verify=self.verify)
        client = OAuth2Session(self._connections[CLIENT_ID],
                               token=token,
                               auto_refresh_url=self._connections[TOKEN_URL],
                               auto_refresh_kwargs={'client_id': self._connections[CLIENT_ID],
                                                    'client_secret': self._connections[CLIENT_SECRET]
                                                    },
                               token_updater=lambda _: self.logger.debug("Updated token."))

        return client

    def _wait_for_response(self, uri: str) -> bytes:
        webbrowser.open(uri)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.logger.info("Please login. Waiting...")
            s.bind(("127.0.0.1", self._connections[PORT]))
            s.listen()
            wait = True
            while wait:
                conn, (client_host, client_port) = s.accept()
                self.logger.debug("Got connection from {} {}".format(client_host, client_port))
                self.logger.info("Authentication complete.")
                data = conn.recv(1000)
                conn.send(b"HTTP/1.0 200 OK\n")
                conn.send(b"Content-Type: text/html\n")
                conn.send(b"\n")
                conn.send(
                    b"""<html><body><h1>Authentication complete</h1><p>Please close this page.</p></body></html>""")
                conn.close()
                wait = False

        return data

    def _parse_response(self, data: str) -> str:
        if "error" in data:
            from http.client import HTTPException
            state, error, description = data.split("&")
            description = description.split("=")[1].split(" ")[0].replace("+", " ")
            error = error.split("=")[-1]
            self.logger.error("Error: {} - {}".format(error, description))
            raise HTTPException(description)
        return data.split("code=")[-1].split(" ")[0].split("&")[0]
