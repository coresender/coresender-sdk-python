__all__ = ['LoginMethod', 'CoresenderClient', 'CoresenderApiRequest']

import base64
import enum
import logging
from abc import abstractmethod
from typing import Optional, Union
from urllib.parse import quote_plus

import httpx

from .. import __version__, errors
from ..token import OAuth2Token
from ..context import CoresenderContext, get_context
from ..http_error_handlers import get_handler as get_error_handler


_logger = logging.getLogger('coresender')
_client: Optional['CoresenderClient'] = None


class LoginMethod(enum.Enum):
    oauth2 = 'oauth2'
    api_key = 'api_key'


class CoresenderClientAuth(httpx.Auth):
    def __init__(self,
        oauth2_token_required: bool, api_key_required: bool,
        access_token: str,
        sending_account_key: str, sending_account_id: str
    ):
        self.oauth2_token_required = oauth2_token_required
        self.api_key_required = api_key_required
        self.access_token = access_token
        self.sending_account_key = sending_account_key
        self.sending_account_id = sending_account_id

    def auth_flow(self, request):
        if self.oauth2_token_required:
            request.headers['Authorization'] = 'Bearer ' + self.access_token
            _logger.debug("Auth: using oauth2 token")
        elif self.api_key_required:
            token = base64.b64encode(b'%s:%s' % (self.sending_account_id.encode(), self.sending_account_key.encode()))
            request.headers['Authorization'] = 'Basic ' + token.decode()
            _logger.debug("Auth: using basic auth")

        yield request


class CoresenderClient:
    def __init__(self, ctx: CoresenderContext):
        self._ctx = ctx

    @classmethod
    def _url_encode(cls, params: dict) -> str:
        r = []
        for key, value in params.items():
            key = quote_plus(key)
            if isinstance(value, (tuple, list)):
                for single_value in value:
                    if single_value is not None:
                        r.append('%s[]=%s' % (key, quote_plus(str(single_value).encode())))
            elif value is not None:
                r.append('%s=%s' % (key, '' if value is None else quote_plus(str(value).encode())))

        r = '&'.join(r)
        return r

    @classmethod
    def _build_url(cls, url: str, params: dict) -> str:
        if params:
            params = cls._url_encode(params)
            if params:
                sign = '&' if '?' in url else '?'
                url += sign + params
        return url

    async def login(self, force: bool = False) -> None:
        if self._ctx.token and self._ctx.token.is_valid() and not force:
            _logger.debug("Reusing saved OAuth2 token")
            return

        login = Login()
        data = {
            "grant_type": "password",
            "email": self._ctx.username,
            "password": self._ctx.password,
        }

        rsp = await self.send(login.api_method, login.get_full_url(), data)
        json_response = rsp.json()
        if 'access_token' in json_response:
            self._ctx.token = OAuth2Token.from_rq_json(json_response)
            _logger.info("Logged in as %s", data['email'])

            self._ctx.token_storage_handler.save(self._ctx.token)
        else:
            raise errors.CoresenderError("Unrecognized response from Coresender API: [%s] %s" % (rsp.status_code, json_response))

    async def send(self, method: str, url: str, data: dict = None, options: dict = None) -> httpx.Response:
        if not options:
            options = {}

        headers = {
            'User-Agent': 'coresender-sdk-python/%s' % __version__,
            'Accept': 'application/json',
        }
        auth = CoresenderClientAuth(
            oauth2_token_required=options.get('oauth2_token_required', False),
            api_key_required=options.get('api_key_required', False),
            access_token=(self._ctx.token.access_token if self._ctx.token else None),
            sending_account_key=self._ctx.sending_account_key,
            sending_account_id=self._ctx.sending_account_id,
        )

        if auth.oauth2_token_required and not auth.access_token:
            await self.login()
            auth.access_token = self._ctx.token.access_token

        if 'headers' in options:
            headers.update(options['headers'])

        url = self._build_url(url, options.get('query_params', {}))
        _logger.debug("Sending %s to %s with headers %s and data %s", method, url, headers, data)

        async with httpx.AsyncClient() as cl:
            rsp = await cl.request(method, url, headers=headers, json=data, auth=auth)

        _logger.debug("Coresender API response is [%s] %s", rsp.status_code, rsp.text)

        error_handler = get_error_handler(rsp)
        if error_handler:
            error_handler()

        return rsp


class CoresenderApiRequest:
    _api_version: str = None
    _api_proto: str = 'https'
    _api_host: str = 'api.coresender.com'
    _api_port: int = 443
    _api_method: str = None
    _api_method_uri: str = None
    _login_required: bool = None
    _login_method: LoginMethod = None

    _client: CoresenderClient = None

    @classmethod
    def client(cls) -> Optional[CoresenderClient]:
        if not cls._client:
            ctx = get_context()
            cls._client = CoresenderClient(ctx)

        return cls._client

    @classmethod
    def set_client(cls, client: CoresenderClient) -> None:
        cls._client = client

    async def send(self, *, data: Union[list, dict] = None, qs: dict = None, headers: dict = None):
        query_params = self.get_query_params() or {}
        if qs:
            query_params.update(qs)

        options = {
            'query_params': query_params,
            'headers': headers or {},
            'api_key_required': (self.login_required and self.login_method is LoginMethod.api_key),
            'oauth2_token_required': (self.login_required and self.login_method is LoginMethod.oauth2),
        }

        query_data = data or self.to_json()

        api_rsp = await self.client().send(self._api_method, self.get_full_url(), query_data, options)

        return api_rsp

    @abstractmethod
    async def execute(self) -> 'CoresenderApiRequest':
        raise NotImplementedError()

    def get_full_url(self) -> str:
        url_prefix = '%(proto)s://%(host)s:%(port)d/v%(version)s/%(uri)s' % {
            'proto': self._api_proto,
            'host': self._api_host,
            'port': self._api_port,
            'version': self._api_version,
            'uri': self._api_method_uri,
        }
        return url_prefix

    def to_json(self) -> Optional[Union[dict, list]]:
        if not hasattr(self, '_to_json'):
            return None
        return self._to_json()

    def get_query_params(self) -> dict:
        return {}

    @property
    def api_method(self) -> str:
        return self._api_method

    @property
    def login_required(self) -> bool:
        return self._login_required

    @property
    def login_method(self) -> Optional[LoginMethod]:
        return self._login_method


class Login(CoresenderApiRequest):
    _api_method: str = 'POST'
    _api_version: str = '1'
    _api_method_uri: str = 'login'
    _login_required: LoginMethod = False
