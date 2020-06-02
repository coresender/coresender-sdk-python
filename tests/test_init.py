import coresender
from coresender import context


def test_context_is_empty():
    assert context.get_context() == None


def test_setup_context():
    acc_key = 'aaa'
    acc_id = 'bbb'
    coresender.init(sending_account_key=acc_key, sending_account_id=acc_id)

    ctx = context.get_context()
    assert type(ctx) is context.CoresenderContext
    assert ctx.sending_account_id == acc_id
    assert ctx.sending_account_key == acc_key
