from mock import patch
import pytest

import coresender
from coresender.requests.core import CoresenderClient


def _get_email_structure(data):
    return {
       'from': {
           'email': data.get('from_email', None),
           'name': data.get('from_name', None),
       },
       'to': [
            {
                'email': data.get('to_email', None),
                'name': data.get('to_name', None),
            }
       ],
       'subject': data.get('subject', None),
       'body': {
           'html': data.get('body_html', None),
           'text': data.get('body_text', None),
       },
       'custom_id': data.get('custom_id', None),
       'custom_id_unique': data.get('custom_id_unique', False),
       'track_opens': data.get('track_opens', False),
       'track_clicks': data.get('track_clicks', False),
       'list_id': data.get('list_id', None),
       'list_unsubscribe': data.get('list_unsubscribe', None),
    }


def _get_emails_structures(data):
    ret = [_get_email_structure(item) for item in data]
    return ret


@pytest.mark.asyncio
async def test_simple_email_missing_required_params(mocker):
    rq = coresender.SendEmail()
    with pytest.raises(coresender.errors.CoresenderError):
        rsp = await rq.simple_email(to_email='to@example.com', subject='test', body='test')

    with pytest.raises(coresender.errors.CoresenderError):
        rsp = await rq.simple_email(from_email='from@example.com', subject='test', body='test')


@patch('coresender.responses.SendEmail')
@pytest.mark.asyncio
async def test_simple_email_send(_, cs_ctx, mocker):
    rq = coresender.SendEmail()
    assert type(rq) is coresender.SendEmail

    client = mocker.patch.object(CoresenderClient(cs_ctx), 'send')

    rq.set_client(client)

    rsp = await rq.simple_email(from_email='from@example.com', to_email='to@example.com', subject='test', body='test')

    client.send.assert_awaited_once()


def test_add_to_batch():
    rq = coresender.SendEmail()
    assert type(rq) is coresender.SendEmail

    emails = [
        {
            'from_email': 'from@example.com',
            'to_email': 'to@example.com',
            'subject': 'test 1',
        },
        {
            'from_email': 'from@example.com',
            'to_email': 'to@example.com',
            'subject': 'test 2',
        },
    ]
    rq.add_to_batch(**emails[0])
    rq.add_to_batch(**emails[1])

    assert rq._emails == _get_emails_structures(emails)


@pytest.mark.asyncio
async def test_batch_send(cs_ctx, mocker):
    cl = mocker.patch.object(CoresenderClient(cs_ctx), 'send')
    mocker.patch('coresender.responses.SendEmail')

    rq = coresender.SendEmail()
    assert type(rq) is coresender.SendEmail

    rq.set_client(cl)

    emails = [
        {
            'from_email': 'from@example.com',
            'to_email': 'to@example.com',
            'subject': 'test 1',
        },
        {
            'from_email': 'from@example.com',
            'to_email': 'to@example.com',
            'subject': 'test 2',
        },
    ]
    rq.add_to_batch(**emails[0])
    rq.add_to_batch(**emails[1])

    rsp = await rq.execute()

    cl.send.assert_awaited_once()
    assert not rq._emails
