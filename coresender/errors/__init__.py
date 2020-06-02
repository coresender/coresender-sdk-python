class CoresenderError(Exception):
    pass


class CoresenderApiError(CoresenderError):
    def __init__(self, response_code, msg):
        self.response_code = response_code
        self.msg = msg

    def __str__(self):
        return self.msg


class AuthorizationError(CoresenderApiError):
    pass


class ValidationError(CoresenderApiError):
    pass


class ApiLogicError(CoresenderApiError):
    pass


class EntityNotFoundError(ApiLogicError):
    pass


class EntityExistsError(ApiLogicError):
    pass
