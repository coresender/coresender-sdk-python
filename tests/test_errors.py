import pytest

from coresender import http_error_handlers as handlers
from coresender import errors


def test_default_error(mocker):
    rsp = mocker.patch('httpx.Response')
    rsp.status_code = 447
    rsp_json = {'data': {'code': '', 'errors': [{'code': 'A', 'description': 'desc'}]}}
    rsp.json = mocker.MagicMock(return_value=rsp_json)

    handler = handlers.get_handler(rsp)
    assert type(handler) is handlers.ErrorHandlerDefault

    with pytest.raises(errors.CoresenderApiError):
        handler()


def test_auth_error(mocker):
    rsp = mocker.patch('httpx.Response')
    rsp.status_code = 401
    rsp_json = {'data': {'code': '', 'errors': [{'code': 'AUTHORIZATION_ERROR', 'description': 'Invalid credentials'}]}}
    rsp.json = mocker.MagicMock(return_value=rsp_json)

    handler = handlers.get_handler(rsp)
    assert type(handler) is handlers.ErrorHandler401

    with pytest.raises(errors.AuthorizationError):
        handler()


def test_validation_error(mocker):
    rsp = mocker.patch('httpx.Response')
    rsp.status_code = 422
    rsp_json = {
        'data': {
            'code': '',
            'errors': [
                {
                    'field': 'email',
                    'errors': [
                        {
                            'code': 'INVALID_EMAIL',
                            'description': 'invalid email address',
                        }
                    ]
                }
            ]
        }
    }
    rsp.json = mocker.MagicMock(return_value=rsp_json)

    handler = handlers.get_handler(rsp)
    assert type(handler) is handlers.ErrorHandler422

    with pytest.raises(errors.ValidationError):
        handler()
