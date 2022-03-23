__all__ = ["init"]
__version__ = '1.1.1'

import logging
import os

from . import token
from . import context
from . import errors
from .requests import *


_logger = logging.getLogger('coresender')
_logger.addHandler(logging.NullHandler())


def init(
    *,
    sending_account_key: str = None, sending_account_id: str = None,
    api_proto: str = None, api_host: str = None, api_port: int = None,
    debug: bool = False):

    ctx = context.CoresenderContext()
    ctx.sending_account_key = sending_account_key or os.environ.get('CORESENDER_SENDING_API_KEY')
    ctx.sending_account_id = sending_account_id or os.environ.get('CORESENDER_SENDING_API_ID')
    if not api_proto:
        ctx.api_proto = api_proto
    if api_host:
        ctx.api_host = api_host
    if api_port:
        ctx.api_port = api_port

    context.set_context(ctx)

    if debug or os.environ.get('CORESENDER_DEBUG', '').lower() in ('yes', 'true', '1'):
        configure_debug_logger()


def configure_debug_logger():
    import sys

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'))
    _logger.addHandler(handler)
    _logger.setLevel(logging.DEBUG)
