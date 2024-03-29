__all__ = ["CoresenderContext", "get_context", "set_context"]

from typing import Optional


_ctx: Optional['CoresenderContext'] = None


class CoresenderContext:
    def __init__(self):
        self.token = None
        self.token_storage = None
        self.token_storage_params = {}
        self.token_storage_handler = None
        self.username = None
        self.password = None
        self.sending_account_key = None
        self.sending_account_id = None
        self.api_proto = None
        self.api_host = None
        self.api_port = None

    def __repr__(self):
        return ('<CoresenderContext token="%s", token_storage="%s", username="%s", password="***", '
               'sending_account_id="%s", sending_account_key="***", api_proto="%s", api_host="%s", '
                'api_port="%s">') % (
            self.token,
            self.token_storage,
            self.username,
            self.sending_account_id,
            self.api_proto,
            self.api_host,
            self.api_port,
        )


def get_context() -> Optional[CoresenderContext]:
    return _ctx


def set_context(ctx: CoresenderContext):
    global _ctx
    _ctx = ctx
