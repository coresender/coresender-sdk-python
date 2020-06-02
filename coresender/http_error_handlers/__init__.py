__all__ = ['get_handler']

import logging
from typing import Callable, Optional

import httpx

from .. import errors

_logger = logging.getLogger('coresender')
_error_handlers = {}


def get_handler(rsp: httpx.Response) -> Optional[Callable[[], None]]:
    handler = None
    http_code = str(rsp.status_code)
    if http_code in _error_handlers:
        handler = _error_handlers[http_code]
    elif http_code[0] in _error_handlers:
        handler = _error_handlers[http_code[0]]
    else:
        # if it's not json or there is no `code` key - both situations handle in same way
        try:
            data = rsp.json()
            handler = _error_handlers.get(data['data']['code'], None)
        except:
            pass

    if not handler and http_code[0] != '2':
        handler = _error_handlers['default']

    if not handler:
        return

    return handler(rsp.status_code, rsp)


class ErrorHandler:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        global _error_handlers
        _error_handlers[cls.register_code] = cls

    def __init__(self, http_code: int, rsp: httpx.Response):
        self._http_code = http_code
        self._rsp = rsp


class ErrorHandlerDefault(ErrorHandler):
    register_code = 'default'

    def __call__(self):
        data = self._rsp.json()
        _logger.error("Coresender API response code is %s and data: %s", self._http_code, data)
        raise errors.CoresenderApiError(data['data']['code'], "Coresender API request failed, http status code: %s" % self._http_code)


class ErrorHandler401(ErrorHandler):
    register_code = '401'

    def __call__(self):
        _logger.error("Coresender API authorization error: [%s] %s", self._http_code, self._rsp.json())
        data = self._rsp.json()['data']['errors'][0]

        raise errors.AuthorizationError(data['code'], data['description'])


class ErrorHandler422(ErrorHandler):
    register_code = '422'

    def __call__(self):
        _logger.error("Coresender API validation error: [%s] %s", self._http_code, self._rsp.json())
        data = self._rsp.json()['data']

        msg = []
        for error in data['errors']:
            msg.append('field %s' % error['field'])
            items = ['%s: %s' % (item['code'], item['description']) for item in error['errors']]
            if items:
                msg[-1] += ': ' + ', '.join(items)

        raise errors.ValidationError(data['code'], '. '.join(msg))


class ErrorHandler409(ErrorHandler):
    register_code = '409'

    _exceptions = {
        'ENTITY_EXISTS': errors.EntityExistsError,
    }

    def __call__(self):
        _logger.error("Coresender API error: [%s] %s", self._http_code, self._rsp.json())
        data = self._rsp.json()['data']

        # there can be messing 'code' in data or missing code in _exceptions, both handled in same way
        try:
            exc_class = self._exceptions[data['code']]
        except KeyError:
            exc_class = errors.ApiLogicError

        msg = ['%s: %s' % (error['code'], error['description']) for error in data['errors']]
        raise exc_class(data['code'], '. '.join(msg))
