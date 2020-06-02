__all__ = ["OAuth2Token", "get_storage_handler"]

import datetime
import json
import logging
import pathlib
from abc import abstractmethod
from typing import Optional, Type

from . import errors


_logger = logging.getLogger('coresender')
_storage_handlers = {}


def get_storage_handler(name: str) -> Type['OAuth2TokenStorage']:
    try:
        token_storage = _storage_handlers[name]
    except KeyError:
        raise errors.CoresenderError("Unknown token storage: %s" % name)

    return token_storage


class OAuth2Token:
    __slots__ = ('_token_type', '_expires_on', '_access_token', '_refresh_token')

    def __init__(self):
        self._token_type = None
        self._expires_on = None
        self._access_token = None
        self._refresh_token = None

    def is_valid(self) -> bool:
        return self.expires_on > datetime.datetime.now()

    @property
    def token_type(self) -> Optional[str]:
        return self._token_type

    @token_type.setter
    def token_type(self, value: str):
        self._token_type = str(value)

    @property
    def expires_on(self) -> Optional[datetime.datetime]:
        return self._expires_on

    @expires_on.setter
    def expires_on(self, value: datetime.datetime):
        self._expires_on = value

    def expire_in(self, value: str):
        self.expires_on = datetime.datetime.now() + datetime.timedelta(seconds=int(value))

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value

    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str):
        self._refresh_token = value

    @classmethod
    def from_rq_json(cls, data: dict) -> 'OAuth2Token':
        r = cls()
        r.access_token = data['access_token']
        r.refresh_token = data['refresh_token']
        r.token_type = data['token_type']
        r.expire_in(data['expires_in'])
        return r

    @classmethod
    def from_json(cls, data: dict) -> 'OAuth2Token':
        r = cls()
        r.access_token = data['access_token']
        r.refresh_token = data['refresh_token']
        r.token_type = data['token_type']
        r.expires_on = datetime.datetime.fromisoformat(data['expires_on'])
        return r

    def to_json(self) -> dict:
        json = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_on': self.expires_on.isoformat(),
        }
        return json

    def __repr__(self):
        r = ', '.join(['%s="%s"' % (item[1:], getattr(self, item)) for item in self.__slots__])
        r = '<OAuth2Token ' + r + '>'
        return r


class OAuth2TokenStorage:
    def __init_subclass__(cls, storage_name: str, **kwargs):
        super().__init_subclass__(**kwargs)

        global _storage_handlers
        _storage_handlers[storage_name] = cls

    def __init__(self, params: dict):
        self.params = params

    @abstractmethod
    def read(self) -> Optional[OAuth2Token]:
        raise NotImplementedError()

    @abstractmethod
    def save(self, token: OAuth2Token) -> None:
        raise NotImplementedError()


class OAuth2TokenFileStorage(OAuth2TokenStorage, storage_name='file'):
    default_storage_path = '~/.coresender.token'

    def _get_path(self):
        path = self.params.get('path', self.default_storage_path)
        path = pathlib.Path(path).expanduser()
        return path

    def read(self) -> Optional[OAuth2Token]:
        path = self._get_path()
        if not path.exists():
            return

        with path.open('r') as fh:
            try:
                token = json.load(fh)
            except Exception as exc:
                _logger.exception("Cannot read saved token from %s", path, exc_info=exc)
                return

        token = OAuth2Token.from_json(token)
        _logger.debug("Success reading cached token data from %s", path)
        return token

    def save(self, token: OAuth2Token) -> None:
        path = self._get_path()
        with path.open('w') as fh:
            json.dump(token.to_json(), fh)
            _logger.debug("OAuth2Token successfully dumped into %s" % path)
