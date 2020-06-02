import pytest

from coresender.context import CoresenderContext
from coresender.requests.core import CoresenderClient


@pytest.fixture
def cs_ctx():
    acc_key = 'aaa'
    acc_id = 'bbb'

    ctx = CoresenderContext()
    ctx.sending_account_id=acc_id
    ctx.sending_account_key=acc_key

    return ctx


@pytest.fixture
def cs_client(cs_ctx):
    return CoresenderClient(cs_ctx)
